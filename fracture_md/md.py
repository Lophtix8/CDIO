from ase.io import read
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from ase.md.verlet import VelocityVerlet
from ase import units
from asap3 import Trajectory

import read_config
import sys, os, yaml
import numpy as np
import logging
from asap3 import EMT

logger = logging.getLogger(__name__)

def calcenergy(a):
    epot = a.get_potential_energy() / len(a)
    ekin = a.get_kinetic_energy() / len(a)
    int_T = ekin / (1.5 * units.kB)
    etot = epot + ekin
    return epot, ekin, int_T, etot

def run_md(supercell_path: str, temp: float, num_steps: int, strain_rate: int):
    """This function runs a molecular dynamics simulation and deposits the result in the 
    folder named "Simulation_results".
    
    Args:
        supercell_file (str): Name of the filename for the supercell
        temp (float): Set temperature in Kelvin for the simulation.
        num_steps (int): Number of simulation steps.
        strain_rate (int): Strain rate

    """
        
    # Set up crystal
    crystal = read(supercell_path)
    supercell_file = os.path.basename(supercell_path)
    
    # Describe the interatomic interactions with the Effective Medium Theory
    crystal.calc = EMT()
    
    # Set the momenta corresponding to T=300K
    MaxwellBoltzmannDistribution(crystal, temperature_K=temp)
    
    # We want to run MD with constant energy using the VelocityVerlet algorithm.
    dyn = VelocityVerlet(crystal, 5 * units.fs)  # 5 fs time step.
    
    dest_path = os.path.dirname(supercell_path) + "/Simulation_results/"
    os.makedirs(dest_path, exist_ok=True)
    resultdata_file_name = "{file_name}.traj"
    traj = Trajectory(dest_path + resultdata_file_name.format(file_name = supercell_file.removesuffix('.poscar') + f"_{temp}K"), "w", crystal)
    dyn.attach(traj.write, interval=10)

    # Function to incrementally apply strain in the z-direction
    def apply_incremental_strain():
        strain_matrix = np.eye(3)  # Identity matrix
        strain_matrix[2, 2] += strain_rate  # Apply strain in z-direction
        crystal.set_cell(crystal.cell @ strain_matrix, scale_atoms=True)  # Scale cell and atom positions

    # Attach strain application to dynamics at every step
    dyn.attach(apply_incremental_strain, interval=1)


    def printenergy(a=crystal):  # store a reference to atoms in the definition.
        """Function to print the potential, kinetic and total energy."""
        epot, ekin, int_T, etot = calcenergy(a)
        print('Energy per atom: Epot = %.3feV  Ekin = %.3feV (T=%3.0fK)'
              'Etot = %.3feV' % (epot, ekin, int_T, etot))
    
    # Run the dynamics
    dyn.attach(printenergy, interval=10)
    printenergy()
    dyn.run(num_steps)

 
if __name__ == "__main__":
    poscar_path = sys.argv[1]
    config_path = sys.argv[2]

    config_data = read_config.main(config_path)[0]
    
    temp = config_data['temps'][0]
    iterations = config_data['iterations']
    
    run_md(poscar_path, temp, iterations, 0.01)
