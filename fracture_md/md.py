from ase.io import read
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from ase.md.verlet import VelocityVerlet
from ase.md.langevin import Langevin
from ase import units
from asap3 import Trajectory

import logging
import logging.config
from fracture_md import setup_logging
import read_config
import sys, os
import numpy as np
from ase.calculators.kim.kim import KIM

logger = logging.getLogger("md")
    

def calcenergy(a):
    """A function that calculates the total, potential and kinetic energy as well as the 
    instantaneous temperature of the crystal

    Args:
        a (atom): The atom object, or crystal, of which the energies and temperature should
        be calculated.

    Returns:
        epot, ekin, int_T, etot (floats): The calculated quantities.
    """
    epot = a.get_potential_energy() / len(a)
    ekin = a.get_kinetic_energy() / len(a)
    int_T = ekin / (1.5 * units.kB)
    etot = epot + ekin
    return epot, ekin, int_T, etot
    

def run_md(supercell_path: str, temp: int, num_steps: int, strain_rate: float, strain_interval: int, t_interval: int, relaxation_iterations: int, potential_id: str, stress_plane: list[int]):

    """This function runs a molecular dynamics simulation and deposits the result in the 
    folder named "Simulation_results".
    
    Args:
        supercell_file (str): Name of the filename for the supercell
        temp (int): Set temperature in Kelvin for the simulation.
        num_steps (int): Number of simulation steps.
        strain_rate (float): Strain rate

    """
    logger.info("Starting md program.")
        
    # Set up crystal
    print(supercell_path)
    crystal = read(supercell_path)
    supercell_file = os.path.basename(supercell_path)
    
    # Describe the interatomic interactions with a potential-id from OpenKim.
    
    logger.info("Setting up interatomic potential.")
    try:
        calc = KIM(potential_id)
        crystal.calc = calc
    except:
        logger.error(f"Could not find the potential-id '{potential_id}' that was given.")
        return
    
    # Set the momenta corresponding to T=300K
    MaxwellBoltzmannDistribution(crystal, temperature_K=temp)
    
    # Relax the fractured system by running MD without strain in the beginning.
    dyn_relax = Langevin(crystal, timestep= 5 * units.fs, temperature_K=temp, friction=0.01/units.fs)
    
    # We want to run MD with constant energy using the VelocityVerlet algorithm.
    dyn = dyn_relax = Langevin(crystal, timestep= 5 * units.fs, temperature_K=temp, friction=0.01/units.fs) # 5 fs time step.
    
    dest_path = os.path.dirname(supercell_path) + "/Simulation_results/"
    os.makedirs(dest_path, exist_ok=True)
    resultdata_file_name = "{file_name}.traj"
    traj = Trajectory(dest_path + resultdata_file_name.format(file_name = supercell_file.removesuffix('.poscar') + f"_{temp}K"), "w", crystal)
    
    dyn_relax.attach(traj.write, interval=10)
    dyn.attach(traj.write, interval=10)

    # Function to incrementally apply strain in the z-direction
    def apply_incremental_strain():
        """Function that applies incremental strain in the z-direction."""
        strain_matrix = np.eye(3)  # Identity matrix
        for i in range(3):
            strain_matrix[i, i] += stress_plane[i]*strain_rate  # Apply strain in z-direction
        crystal.set_cell(crystal.cell @ strain_matrix, scale_atoms=True)  # Scale cell and atom positions
    
    # Attach strain application to dynamics at every step
    dyn.attach(apply_incremental_strain, interval=strain_interval)

    def printenergy(a=crystal):  # store a reference to atoms in the definition.
        """Function to print the potential, kinetic and total energy of the crystal."""
        epot, ekin, int_T, etot = calcenergy(a)
        print('Energy per atom: Epot = %.3feV  Ekin = %.3feV (T=%3.0fK)'
              'Etot = %.3feV' % (epot, ekin, int_T, etot))
    
    # Run the dynamics
    
    # Relaxation
    logger.info("Relaxing the system to reach equilibrium.")
    dyn_relax.attach(printenergy, interval=10)
    dyn_relax.run(relaxation_iterations)
    
    # Straining
    logger.info("Straining the system.")
    dyn.attach(printenergy, interval=10)
    dyn.run(num_steps)

 
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
    stress_plane = [int(x) for x in config_data['stress_plane']]
    setup_logging.setup_logging('md_logging.conf')
    run_md(poscar_path, temp, iterations, strain_rate, strain_interval, t_interval, relaxation_iterations, potential_id, stress_plane)
