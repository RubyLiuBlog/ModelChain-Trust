#!/bin/bash

# 目标目录
TARGET_DIR="/home/bugsmith/model_evaluate_demo/models/qwen_local"
# 源目录
SOURCE_DIR="/home/bugsmith/.cache/huggingface/hub/models--Qwen--Qwen1.5-0.5B-Chat/blobs"

# 复制配置文件
cp "${SOURCE_DIR}/f0041555808f66af0491fa912882f59ed29ed414" "${TARGET_DIR}/config.json"
cp "${SOURCE_DIR}/4ec054254ec0f33b475f9e84d400782704a95014" "${TARGET_DIR}/generation_config.json"
cp "${SOURCE_DIR}/20024bfe7c83998e9aeaf98a0cd6a2ce6306c2f0" "${TARGET_DIR}/merges.txt"
cp "${SOURCE_DIR}/72453a8ccb338811935ab95a3a6ffa86b586807bf5b3dc327f28b5389b5636e6" "${TARGET_DIR}/model.safetensors"
cp "${SOURCE_DIR}/33ea6c72ebb92a237fa2bdf26c5ff16592efcdae" "${TARGET_DIR}/tokenizer.json"
cp "${SOURCE_DIR}/ff55d7b9eb1384e5d4d7e75dc0f564c1a8833d6e" "${TARGET_DIR}/tokenizer_config.json"
cp "${SOURCE_DIR}/4783fe10ac3adce15ac8f358ef5462739852c569" "${TARGET_DIR}/vocab.json"

echo "所有文件已复制到 ${TARGET_DIR}"
ls -lh "${TARGET_DIR}" 