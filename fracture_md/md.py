"""
 Copyright (c) 2024 JALL-E
 Licensed under the MIT License. See LICENSE file in the project root for details.
"""

from ase.io import read
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from ase.md.verlet import VelocityVerlet
from ase.md.langevin import Langevin
from ase.md.nptberendsen import NPTBerendsen
from ase import units
from asap3 import Trajectory

import logging
import logging.config
from fracture_md import setup_logging
import read_config, process_data
import sys, os
import numpy as np
import copy
from ase.calculators.kim.kim import KIM

logger = logging.getLogger("md")
    

def calcenergy(a, stress_plane, starting_size):
    """A function that calculates the total, potential and kinetic energy as well as the 
    instantaneous temperature of the crystal

    Args:
        a (atom): The atom object, or crystal, of which the energies and temperature should
        be calculated.

    Returns:
        epot, ekin, int_T, etot (floats): The calculated quantities.
    """
    atom_num = len(a)
    curr_size = a.get_cell()
    traj_property = {"ekin": a.get_kinetic_energy()/atom_num,
                    "epot": a.get_potential_energy()/atom_num,
                    "etot": a.get_total_energy()/atom_num,
                    "stress": a.get_stress(voigt=False)/units.GPa,
                    "strain": np.subtract(np.divide(curr_size,starting_size), 1),
                    "cell": curr_size,
                    "positions": a.get_positions()}

        # Derived properties.
    traj_property["temperature"] = traj_property["ekin"] / (1.5 * units.kB)
    return traj_property
    

def run_md(supercell_path: str, temp: int, num_steps: int, strain_rate: float, strain_interval: int, t_interval: int, relaxation_iterations: int, potential_id: str, stress_plane: list[int], relaxation_rate: float):

    """This function runs a molecular dynamics simulation and deposits the result in the 
    folder named "Simulation_results".
    
    Args:
        supercell_file (str): Name of the filename for the supercell
        temp (int): Set temperature in Kelvin for the simulation.
        num_steps (int): Number of simulation steps.
        strain_rate (float): Strain rate

    """
    supercell_file = os.path.basename(supercell_path)
    logger.info(f"Starting md program for {supercell_file}.")
        
    # Set up crystal
    print(supercell_path)
    crystal = read(supercell_path)
    original_crystal = copy.deepcopy(crystal)
    # Describe the interatomic interactions with a potential-id from OpenKim.
    
    logger.info(f"Setting up interatomic potential for {supercell_file}.")
    try:
        calc = KIM(potential_id)
        crystal.calc = calc
        original_crystal.calc = calc
    except:
        logger.error(f"Could not find the potential-id '{potential_id}' that was given.")
        return
    
    # Set the momenta corresponding to T=300K
    MaxwellBoltzmannDistribution(crystal, temperature_K=temp)
    
    # Relax the fractured system by running MD without strain in the beginning.
    #dyn_relax = NPTBerendsen(crystal, timestep= 5 * units.fs, temperature_K=temp, pressure_au=1.013*units.bar)
    dyn_relax = Langevin(crystal, timestep= 5 * units.fs, temperature_K=temp, friction=0.01/units.fs) # 5 fs time step.
    # We want to run MD with constant energy using the VelocityVerlet algorithm.
    dyn = Langevin(crystal, timestep= 5 * units.fs, temperature_K=temp, friction=0.01/units.fs) # 5 fs time step.
    
    dest_path = os.path.dirname(supercell_path) + "/Simulation_results"
    
    os.makedirs(dest_path, exist_ok=True)
    
    file_name = supercell_file.removesuffix('.poscar') + f"_{''.join([str(x) for x in stress_plane])}_{temp}K"
    traj_filepath = os.path.join(dest_path, f"{file_name}.traj")
    pkl_filepath = traj_filepath.removesuffix(".traj")+".pkl"
    
    traj = Trajectory(traj_filepath, "w", crystal)
    
    dyn_relax.attach(traj.write, interval=10)
    dyn.attach(traj.write, interval=10)

    # Function to incrementally apply strain in the z-direction
    def apply_incremental_strain():
        """Function that applies incremental strain in the direction provided by the strain tensor."""
        strain_matrix = np.eye(3)  # Identity matrix
        for i in range(3):
            strain_matrix[i, i] += stress_plane[i]*strain_rate  # Apply strain in z-direction
        crystal.set_cell(crystal.cell @ strain_matrix, scale_atoms=True)  # Scale cell and atom positions
    
    # Attach strain application to dynamics at every step

    def printenergy(a=crystal):  # store a reference to atoms in the definition.
        """Function to print the potential, kinetic and total energy of the crystal."""
        traj_property = calcenergy(a, stress_plane, starting_size)
        traj_properties.append(traj_property)
        process_data.write_to_pkl(traj_properties, pkl_filepath)
        epot, ekin, int_T, etot = traj_property['epot'], traj_property['ekin'], traj_property['temperature'], traj_property['etot']
        print('Energy per atom: Epot = %.3feV  Ekin = %.3feV (T=%3.0fK)'
              'Etot = %.3feV' % (epot, ekin, int_T, etot))
    
    # Run the dynamics
    atom_num = len(crystal)
    stress = sum(crystal.get_stress()[i] for i in range(3))

    relaxed_system_properties = {"cur_dir": -np.sign(stress), "prev_dir":-np.sign(stress)}
    # Relaxation
    def relax_system(a = crystal, rsp = relaxed_system_properties):

        # Using stress
        stress = sum([a.get_stress()[i] for i in range(3)])
        rsp['prev_dir'] = copy.deepcopy(rsp['cur_dir'])
        rsp['cur_dir'] = dir = -np.sign(stress)
        
        print(f"stress: {stress}, cur_dir: {rsp['cur_dir']} prev_dir: {rsp['prev_dir']}")
        a.cell *= (1+relaxation_rate*dir)

        # Using total energy
        """
        cur_epot = rsp['cur_epot'] = a.get_total_energy()/atom_num
        prev_epot = rsp['prev_epot']
        ratio = abs((cur_epot-prev_epot)/prev_epot) 
        if ratio > strain_rate:
            ratio = strain_rate
        if cur_epot > prev_epot:
            rsp['dir'] *= -1
        print(f"etot: {cur_epot}, ratio: {ratio}, dir: {rsp['dir']}")
        a.cell *= (1+ratio*rsp['dir'])
        rsp['prev_epot'] = cur_epot"""


    dyn_relax.attach(relax_system, interval=10)
    logger.info(f"Relaxation of {supercell_file}.")
    #dyn_relax.attach(printenergy, interval=10)
    dir_same = relaxed_system_properties['cur_dir'] == relaxed_system_properties['prev_dir']
    while (dir_same and relaxation_iterations > 0):
        dyn_relax.run(10)
        dir_same = relaxed_system_properties['cur_dir'] == relaxed_system_properties['prev_dir']
        relaxation_iterations -= 10
    
    # Between relaxation and starting the simulation
    starting_size = crystal.get_cell()
    original_crystal.cell*=starting_size
    print(f"Starting size: {starting_size}")
    traj_properties = [calcenergy(original_crystal, stress_plane, starting_size)]

    # Straining
    logger.info(f"Straining of {supercell_file}.")
    dyn.attach(apply_incremental_strain, interval=strain_interval)
    dyn.attach(printenergy, interval=10)
    dyn.run(num_steps)

    process_data.write_to_pkl(traj_properties, pkl_filepath)

    logger.info(f"Done with simulation of {supercell_file}")
 
if __name__ == "__main__":
    poscar_path = sys.argv[1]
    config_path = sys.argv[2]

    config_data = read_config.main(config_path)[0]
    
    temp = config_data['temps'][0]
    iterations = config_data['iterations']
    potential_id = config_data['potential']
    strain_interval = config_data['strain_interval']
    strain_rate = config_data['strain_rate']
    relaxation_iterations = config_data['relaxation_iterations']
    t_interval = config_data['t_interval']
    relaxation_rate = config_data['relaxation_rate']
    stress_plane = [int(x) for x in config_data['stress_plane']]
    setup_logging.setup_logging('md_logging.conf')
    run_md(poscar_path, temp, iterations, strain_rate, strain_interval, t_interval, relaxation_iterations, potential_id, stress_plane, relaxation_rate)
