"""Demonstrates molecular dynamics with constant energy and incremental strain."""

from asap3 import Trajectory
from ase import units
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from ase.md.verlet import VelocityVerlet
from ase.io import read
from ase.calculators.emt import EMT
import numpy as np

def calcenergy(a):
    epot = a.get_potential_energy() / len(a)
    ekin = a.get_kinetic_energy() / len(a)
    int_T = ekin / (1.5 * units.kB)
    etot = epot + ekin
    return epot, ekin, int_T, etot

def run_md(supercell_name):
    use_asap = True
    resultdata_file_name = "{file_name}.traj"

    if use_asap:
        from asap3 import EMT
    else:
        from ase.calculators.emt import EMT

    # Set up a crystal
    atoms = read(supercell_name)

    # Describe the interatomic interactions with the Effective Medium Theory
    atoms.calc = EMT()

    # Set the momenta corresponding to T=300K
    MaxwellBoltzmannDistribution(atoms, temperature_K=300)

    # Set up molecular dynamics with constant energy using the VelocityVerlet algorithm
    dyn = VelocityVerlet(atoms, 5 * units.fs)  # 5 fs time step
    traj = Trajectory(resultdata_file_name.format(file_name=supercell_name.removesuffix('.poscar')), "w", atoms)
    dyn.attach(traj.write, interval=10)

    # Define the strain rate and the number of strain steps
    strain_rate = 0.01  # Strain increment per step
    num_steps = 200  # Number of MD steps

    # Function to incrementally apply strain in the z-direction
    def apply_incremental_strain():
        strain_matrix = np.eye(3)  # Identity matrix
        strain_matrix[2, 2] += strain_rate  # Apply strain in z-direction
        atoms.set_cell(atoms.cell @ strain_matrix, scale_atoms=True)  # Scale cell and atom positions

    # Attach strain application to dynamics at every step
    dyn.attach(apply_incremental_strain, interval=1)

    def printenergy(a=atoms):
        """Function to print the potential, kinetic, and total energy."""
        epot, ekin, int_T, etot = calcenergy(a)
        print(f'Energy per atom: Epot = {epot:.3f} eV  Ekin = {ekin:.3f} eV (T={int_T:.0f} K)  Etot = {etot:.3f} eV')

    # Attach energy printing and run the dynamics
    dyn.attach(printenergy, interval=10)
    printenergy()
    dyn.run(num_steps)

if __name__ == "__main__":
    run_md('fractured_Al_5x10x5.poscar')
