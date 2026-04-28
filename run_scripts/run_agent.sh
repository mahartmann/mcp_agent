#!/bin/bash



# Rename GPUs
source /scratch/hartmann/submit-files/rename_gpus.sh

# Setup conda environment
source /scratch/hartmann/miniconda3/etc/profile.d/conda.sh
echo "Current conda environment: $CONDA_DEFAULT_ENV"
conda activate mcp_agent
export PYTHONPATH=$PYTHONPATH:/nethome/mareikeh/mcp_agent
echo "Activated conda environment: $CONDA_DEFAULT_ENV"

# API keys
source /nethome/mareikeh/mcp_agent/secrets.env


echo "=== CUDA Debugging Information ==="

nvidia-smi
echo "CUDA_HOME: $CUDA_HOME"
echo "CUDA_VISIBLE_DEVICES: $CUDA_VISIBLE_DEVICES"
echo "==================================="
echo "HOSTNAME: $HOSTNAME"
which python

echo "Starting MCP agent"

python agents/vllm_langchain_agent.py
