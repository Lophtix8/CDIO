#!/bin/bash
#
#SBATCH -J tfya99_fracture_md
#SBATCH -A liu-compute-2024-33
#SBATCH --reservation devel
#SBATCH -t 00:30:00
#SBATCH -N 1
#SBATCH -n 32
#SBATCH --exclusive
#
export NSC_MODULE_SILENT=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export OMP_NUM_THREADS=1
