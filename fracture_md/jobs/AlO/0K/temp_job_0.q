#!/bin/bash
#
#SBATCH -J testjob
#SBATCH -A <project>
#SBATCH --reservation devel
#SBATCH -t 00:05:00
#SBATCH -N 1
#SBATCH -n 32
#SBATCH --exclusive
#
export NSC_MODULE_SILENT=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export OMP_NUM_THREADS=1
mpprun echo "Hello world!"
echo "job completed"
python3 /home/adriankjellen/CDIO/fracture_md/md.py jobs/AlO/fractured_Al2O3_5x7x5.poscar jobs/AlO/0K/fractured_Al2O3_5x7x5.poscar_0K.yaml