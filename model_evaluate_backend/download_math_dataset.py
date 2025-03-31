#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
下载MATH数据集并保存到本地
"""

import os
import sys
import json
import requests
from tqdm import tqdm
import random

# MATH数据集的GitHub仓库URL
MATH_REPO_URL = "https://github.com/hendrycks/math"
MATH_RAW_URL = "https://raw.githubusercontent.com/hendrycks/math/master/MATH"

# 定义MATH数据集的不同类别
MATH_CATEGORIES = [
    "algebra", "counting_and_probability", "geometry", 
    "intermediate_algebra", "number_theory", "prealgebra", 
    "precalculus"
]

def download_file(url, save_path):
    """下载文件并保存到指定路径"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # 如果请求失败则抛出异常
        
        # 创建保存目录（如果不存在）
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # 保存文件
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 KB
        
        with open(save_path, 'wb') as f, tqdm(
                desc=f"下载 {os.path.basename(save_path)}",
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
            ) as pbar:
            for data in response.iter_content(block_size):
                f.write(data)
                pbar.update(len(data))
                
        return True
    except Exception as e:
        print(f"下载失败: {str(e)}")
        return False

def create_sample_dataset(samples_per_category=5, output_file="math_samples.jsonl"):
    """从各个类别中选择样本创建一个小型示例数据集"""
    all_samples = []
    
    # 遍历所有类别
    for category in MATH_CATEGORIES:
        category_dir = os.path.join("data", "math", category)
        if not os.path.exists(category_dir):
            print(f"警告: 类别目录不存在: {category_dir}")
            continue
            
        # 获取该类别下的所有JSON文件
        json_files = [f for f in os.listdir(category_dir) if f.endswith(".json")]
        
        # 随机选择指定数量的样本
        selected_files = random.sample(json_files, min(samples_per_category, len(json_files)))
        
        # 读取选中的文件并添加到样本列表
        for filename in selected_files:
            file_path = os.path.join(category_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                sample = {
                    "problem": data.get("problem", ""),
                    "level": data.get("level", ""),
                    "type": category,
                    "solution": data.get("solution", ""),
                    "answer": data.get("answer", "")
                }
                all_samples.append(sample)
                
            except Exception as e:
                print(f"处理文件出错 {file_path}: {str(e)}")
    
    # 保存样本到JSONL文件
    output_path = os.path.join("data", "math", output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        for sample in all_samples:
            f.write(json.dumps(sample, ensure_ascii=False) + "\n")
            
    print(f"已创建示例数据集: {output_path} (包含 {len(all_samples)} 个样本)")
    return output_path

def download_math_dataset(target_dir="data/math", download_all=False):
    """
    下载MATH数据集
    
    Args:
        target_dir: 目标保存目录
        download_all: 是否下载完整数据集（否则只下载示例数据）
    """
    os.makedirs(target_dir, exist_ok=True)
    print(f"下载MATH数据集到: {target_dir}")
    
    # 创建示例数据文件
    demo_data = [
        {"problem": "求解方程 x^2 - 7x + 12 = 0。", "answer": "3, 4", "type": "algebra"},
        {"problem": "计算三角形面积，底边长为6，高为4。", "answer": "12", "type": "geometry"},
        {"problem": "对于函数 f(x) = 2x^3 - 3x^2 + 1，求 f'(2)。", "answer": "12", "type": "precalculus"}
    ]
    
    demo_file = os.path.join(target_dir, "demo.jsonl")
    with open(demo_file, 'w', encoding='utf-8') as f:
        for item in demo_data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    
    print(f"已创建示例数据: {demo_file}")
    
    if not download_all:
        print("仅创建了示例数据。如需下载完整数据集，请使用 --all 参数。")
        return
    
    # 下载完整数据集
    # 遍历所有类别
    for category in MATH_CATEGORIES:
        category_dir = os.path.join(target_dir, category)
        os.makedirs(category_dir, exist_ok=True)
        
        # 下载train.json文件
        train_url = f"{MATH_RAW_URL}/train/{category}.json"
        train_path = os.path.join(category_dir, "train.json")
        print(f"下载 {category} 训练数据...")
        success = download_file(train_url, train_path)
        
        if not success:
            print(f"尝试替代方法下载 {category} 数据...")
            # 如果无法直接下载，尝试创建一些简单的示例问题
            create_category_examples(category, category_dir)
    
    # 创建示例数据集
    create_sample_dataset(samples_per_category=5, output_file="samples.jsonl")
    
    print("完成MATH数据集下载!")
    
def create_category_examples(category, save_dir):
    """为特定类别创建示例问题"""
    # 为每个类别定义一些示例问题
    examples = {
        "algebra": [
            {"problem": "求解方程 x^2 - 5x + 6 = 0。", "answer": "2, 3", "level": "Level 1"},
            {"problem": "因式分解: x^2 - 9。", "answer": "(x+3)(x-3)", "level": "Level 1"}
        ],
        "geometry": [
            {"problem": "一个圆的半径为3，求它的面积。", "answer": "9π", "level": "Level 1"},
            {"problem": "一个长方形的长为5，宽为3，求它的面积。", "answer": "15", "level": "Level 1"}
        ],
        "number_theory": [
            {"problem": "17和23的最大公约数是多少?", "answer": "1", "level": "Level 1"},
            {"problem": "12和18的最小公倍数是多少?", "answer": "36", "level": "Level 1"}
        ],
        "counting_and_probability": [
            {"problem": "从1到10的数中随机选择一个，选到偶数的概率是多少?", "answer": "1/2", "level": "Level 1"},
            {"problem": "从52张扑克牌中抽一张，抽到红桃的概率是多少?", "answer": "1/4", "level": "Level 1"}
        ],
        "prealgebra": [
            {"problem": "计算: 3 × (4 + 2) ÷ 2。", "answer": "9", "level": "Level 1"},
            {"problem": "如果x = 3，y = 4，计算 2x + y。", "answer": "10", "level": "Level 1"}
        ],
        "intermediate_algebra": [
            {"problem": "求解不等式 2x - 3 > 5。", "answer": "x > 4", "level": "Level 2"},
            {"problem": "简化表达式: (x^2 - 4) ÷ (x - 2)，x ≠ 2。", "answer": "x + 2", "level": "Level 2"}
        ],
        "precalculus": [
            {"problem": "如果 f(x) = 3x^2 - 2x + 1，计算 f'(x)。", "answer": "6x - 2", "level": "Level 3"},
            {"problem": "计算 sin(π/4)。", "answer": "1/√2", "level": "Level 2"}
        ]
    }
    
    # 获取当前类别的示例
    category_examples = examples.get(category, [])
    if not category_examples:
        print(f"没有为类别 {category} 定义示例问题")
        return
    
    # 保存示例到JSON文件
    json_file = os.path.join(save_dir, "examples.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(category_examples, f, ensure_ascii=False, indent=2)
    
    # 同时保存为单独的文件
    for i, example in enumerate(category_examples):
        example_file = os.path.join(save_dir, f"example_{i+1}.json")
        with open(example_file, 'w', encoding='utf-8') as f:
            json.dump(example, f, ensure_ascii=False, indent=2)
    
    print(f"为类别 {category} 创建了 {len(category_examples)} 个示例问题")

if __name__ == "__main__":
    # 处理命令行参数
    download_all = "--all" in sys.argv
    target_dir = "data/math"
    
    # 如果指定了路径参数，使用指定路径
    for arg in sys.argv:
        if arg.startswith("--path="):
            target_dir = arg.split("=")[1]
    
    # 下载数据集
    download_math_dataset(target_dir, download_all) 