#!/bin/bash



# Rename GPUs
source /scratch/hartmann/submit-files/rename_gpus.sh

# Setup conda environment
source /scratch/hartmann/miniconda3/etc/profile.d/conda.sh
echo "Current conda environment: $CONDA_DEFAULT_ENV"

conda activate mcp_agent
pip install -r /nethome/mareikeh/mcp_agent/requirements.txt

# install ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen3.5:0.8b

echo "Activated conda environment: $CONDA_DEFAULT_ENV"

echo "=== CUDA Debugging Information ==="

nvidia-smi
echo "CUDA_HOME: $CUDA_HOME"
echo "CUDA_VISIBLE_DEVICES: $CUDA_VISIBLE_DEVICES"
echo "==================================="
echo "HOSTNAME: $HOSTNAME"
which python

