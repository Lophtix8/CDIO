from ase.io import read
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from ase.md.verlet import VelocityVerlet
from ase import units
from asap3 import Trajectory
import numpy as np
import logging
from ase.calculators.kim.kim import KIM

logger = logging.getLogger(__name__)

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
    

def run_md(supercell_file: str, temp: float, num_steps: int, strain_rate: int, potential_id):
    """This function runs a molecular dynamics simulation and deposits the result in the 
    folder named "Simulation_results".
    
    Args:
        supercell_file (str): Name of the filename for the supercell
        temp (float): Set temperature in Kelvin for the simulation.
        num_steps (int): Number of simulation steps.
        strain_rate (int): Strain rate

    """
    logger.info("Starting md program.")
    file_path = 'Fractured_supercells/'
        
    # Set up crystal
    crystal = read(file_path + supercell_file)
    
    # Describe the interatomic interactions with a potential-id from OpenKim.
    
    logger.info("Setting up interatomic potential.")
    try:
        crystal.calc = calc
        calc = KIM(potential_id)
    except:
        logger.error("Could not find the potential-id that was given.")
        return
    
    # Set the momenta corresponding to T=300K
    MaxwellBoltzmannDistribution(crystal, temperature_K=temp)
    
    # Relax the fractured system by running MD without strain in the beginning.
    dyn_relax = VelocityVerlet(crystal, 5 * units.fs)
    
    # We want to run MD with constant energy using the VelocityVerlet algorithm.
    dyn = VelocityVerlet(crystal, 5 * units.fs)  # 5 fs time step.
    
    resultdata_file_name = "{file_name}.traj"
    traj = Trajectory('Simulation_results/' + resultdata_file_name.format(file_name = supercell_file.removesuffix('.poscar')), "w", crystal)
    
    dyn_relax.attach(traj.write, interval=10)
    dyn.attach(traj.write, interval=10)

    # Function to incrementally apply strain in the z-direction
    def apply_incremental_strain():
        """Function that applies incremental strain in the z-direction."""
        strain_matrix = np.eye(3)  # Identity matrix
        strain_matrix[2, 2] += strain_rate  # Apply strain in z-direction
        crystal.set_cell(crystal.cell @ strain_matrix, scale_atoms=True)  # Scale cell and atom positions

    # Attach strain application to dynamics at every step
    dyn.attach(apply_incremental_strain, interval=1)

    def printenergy(a=crystal):  # store a reference to atoms in the definition.
        """Function to print the potential, kinetic and total energy of the crystal."""
        epot, ekin, int_T, etot = calcenergy(a)
        print('Energy per atom: Epot = %.3feV  Ekin = %.3feV (T=%3.0fK)'
              'Etot = %.3feV' % (epot, ekin, int_T, etot))
    
    # Run the dynamics
    
    # Relaxation
    logger.info("Relaxing the system to reach equilibrium.")
    dyn_relax.attach(printenergy, interval=10)
    dyn_relax.run(100)
    
    # Straining
    logger.info("Straining the system.")
    dyn.attach(printenergy, interval=10)
    dyn.run(num_steps)

 
if __name__ == "__main__":
    potential_id = "EAM_CubicNaturalSpline_ErcolessiAdams_1994_Al__MO_800509458712_002"
    run_md('fractured_Al_5x5x5.poscar', 300, 100, 0.005, potential_id)