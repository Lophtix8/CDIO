from ase.io import read
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from ase.md.verlet import VelocityVerlet
from ase import units
from asap3 import Trajectory
import numpy as np

def calcenergy(a):
    epot = a.get_potential_energy() / len(a)
    ekin = a.get_kinetic_energy() / len(a)
    int_T = ekin / (1.5 * units.kB)
    etot = epot + ekin
    return epot, ekin, int_T, etot

def run_md(supercell_file, fractured = False):
    use_asap = True
    
    if fractured:
        file_path = 'Fractured_supercells/'
    else:
        file_path = 'Supercells/'
    
    # Set up crystal
    crystal = read(file_path + supercell_file)
    
    if use_asap:
        from asap3 import EMT
    else:
        from ase.calculators.emt import EMT
    
    # Describe the interatomic interactions with the Effective Medium Theory
    crystal.calc = EMT()
    
    # Set the momenta corresponding to T=300K
    MaxwellBoltzmannDistribution(crystal, temperature_K=300)
    
    # We want to run MD with constant energy using the VelocityVerlet algorithm.
    dyn = VelocityVerlet(crystal, 5 * units.fs)  # 5 fs time step.
    
    resultdata_file_name = "{file_name}.traj"
    traj = Trajectory(resultdata_file_name.format(file_name = supercell_file.removesuffix('.poscar')), "w", crystal)
    dyn.attach(traj.write, interval=10)

    # Define the strain rate and the number of strain steps
    strain_rate = 0.01  # Strain increment per step
    num_steps = 200  # Number of MD steps

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
    dyn.run(200)

 
if __name__ == "__main__":
	run_md('Al_5x10x5.poscar')
