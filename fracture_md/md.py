from ase.io import read
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from ase.md.verlet import VelocityVerlet
from ase import units
from asap3 import Trajectory
import numpy as np
from asap3 import EMT
from ase.calculators.lammpsrun import LAMMPS
from mace.calculators import mace_mp


def calcenergy(a):
    epot = a.get_potential_energy() / len(a)
    ekin = a.get_kinetic_energy() / len(a)
    int_T = ekin / (1.5 * units.kB)
    etot = epot + ekin
    return epot, ekin, int_T, etot
    

def run_md(supercell_file: str, temp: float, num_steps: int, strain_rate: int):
    """This function runs a molecular dynamics simulation and deposits the result in the 
    folder named "Simulation_results".
    
    Args:
        supercell_file (str): Name of the filename for the supercell
        temp (float): Set temperature in Kelvin for the simulation.
        num_steps (int): Number of simulation steps.
        strain_rate (int): Strain rate

    """
    
    from asap3 import EMT
    file_path = 'Fractured_supercells/'
        
    # Set up crystal
    crystal = read(file_path + supercell_file)
    
    # Describe the interatomic interactions with the Effective Medium Theory
    # crystal.calc = EMT()
    
    # Pbc is by default set to true.
    # crystal.pbc = [False, False, False]
    
    calc = mace_mp(model="small", default_dtype="float32", device="cpu")
    
    crystal.calc = calc
    
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
    
    # Relaxation
    dyn_relax.attach(printenergy, interval=10)
    dyn_relax.run(100)
    
    # Straining
    dyn.attach(printenergy, interval=10)
    printenergy()
    dyn.run(num_steps)

 
if __name__ == "__main__":
    run_md('fractured_Al_5x10x5.poscar', 300, 100, 0.01)