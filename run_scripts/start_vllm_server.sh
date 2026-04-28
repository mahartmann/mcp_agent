#!/usr/bin/env bash

vllm serve /scratch/common_models/$3 --host $1 --port $2 --enable-auto-tool-choice --tool-call-parser hermes
#--max-model-len 100000
