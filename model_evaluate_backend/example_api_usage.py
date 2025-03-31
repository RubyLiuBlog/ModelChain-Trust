#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
模型评测框架API使用示例
"""

import os
import sys
import json

# 设置HuggingFace镜像站点（必须在导入transformers前设置）
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

# 导入API
from model_evaluate_demo.api import (
    evaluate_model,
    list_available_datasets,
    list_available_metrics,
    list_available_model_types,
    get_default_generation_kwargs
)

def main():
    """API使用示例"""
    # 列出可用的组件
    print("可用的数据集:")
    for dataset in list_available_datasets():
        print(f"  - {dataset}")
    
    print("\n可用的评估指标:")
    for metric in list_available_metrics():
        print(f"  - {metric}")
    
    print("\n可用的模型类型:")
    for model_type in list_available_model_types():
        print(f"  - {model_type}")
    
    # 获取默认生成参数
    default_kwargs = get_default_generation_kwargs()
    print("\n默认生成参数:")
    print(json.dumps(default_kwargs, indent=2, ensure_ascii=False))
    
    # 示例：评测一个本地GPT2模型
    model_path = "gpt2"  # 使用huggingface hub中的gpt2
    print(f"\n开始评测模型: {model_path}")
    
    # 可以根据需要修改这些参数
    results = evaluate_model(
        model_path=model_path,
        model_type="huggingface",
        dataset_name="math",
        metrics=["accuracy"],
        max_samples=2,             # 只评测2个样本作为示例
        output_dir="./outputs",
        batch_size=1,
        prompt_template="Solve this math problem:\n{question}\n\nThe answer is:",
        generation_kwargs={
            "temperature": 0.0,
            "max_new_tokens": 50,
            "do_sample": False
        },
        device="cuda",             # 使用GPU，如果没有GPU可以改为"cpu"
        offline=False,             # 允许从HuggingFace下载模型
        debug=True                 # 打印调试信息
    )
    
    # 输出结果
    print("\n评测结果:")
    print(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main() 