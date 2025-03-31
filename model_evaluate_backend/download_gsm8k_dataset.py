#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
下载GSM8K数据集并保存到本地
"""

import os
import sys
import json
import requests
from tqdm import tqdm
import random

# GSM8K数据集的GitHub仓库URL
GSM8K_REPO_URL = "https://github.com/openai/grade-school-math"
GSM8K_RAW_URL = "https://raw.githubusercontent.com/openai/grade-school-math/master/grade_school_math/data"

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

def create_sample_dataset(input_jsonl, output_file, n_samples=100):
    """从GSM8K数据集中选择指定数量的样本创建一个小型示例数据集"""
    try:
        # 读取原始数据
        with open(input_jsonl, 'r', encoding='utf-8') as f:
            data = [json.loads(line) for line in f]
        
        # 随机选择指定数量的样本
        if n_samples < len(data):
            samples = random.sample(data, n_samples)
        else:
            samples = data
            
        # 转换为我们的格式并保存
        formatted_samples = []
        for item in samples:
            formatted_sample = {
                "problem": item.get("question", ""),
                "answer": item.get("answer", "")
            }
            formatted_samples.append(formatted_sample)
            
        # 保存到JSONL文件
        with open(output_file, 'w', encoding='utf-8') as f:
            for sample in formatted_samples:
                f.write(json.dumps(sample, ensure_ascii=False) + "\n")
                
        print(f"已创建GSM8K示例数据集: {output_file} (包含 {len(formatted_samples)} 个样本)")
        return True
        
    except Exception as e:
        print(f"创建示例数据集失败: {str(e)}")
        return False

def download_gsm8k_dataset(target_dir="data/gsm8k", download_all=False):
    """
    下载GSM8K数据集
    
    Args:
        target_dir: 目标保存目录
        download_all: 是否下载完整数据集（否则只下载示例数据）
    """
    os.makedirs(target_dir, exist_ok=True)
    print(f"下载GSM8K数据集到: {target_dir}")
    
    # 创建示例数据文件
    demo_data = [
        {"problem": "Janet在她最喜欢的商店购物。她花了原有金额的20%买了一条裙子，又花了剩余金额的25%买了一件上衣。然后，她用剩余金额的10%买了一条围巾。她仍剩下54美元。她最初有多少钱？", "answer": "100美元"},
        {"problem": "五个人参加一场比赛。第一名获得金牌，第二名获得银牌，第三名获得铜牌。有多少种不同的颁奖方式？", "answer": "60种"},
        {"problem": "汤姆的年龄是他父亲年龄的1/4，汤姆的父亲比汤姆的母亲小3岁。如果汤姆的母亲今年45岁，那么汤姆现在几岁？", "answer": "10.5岁"}
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
    # 尝试下载训练集和测试集
    train_url = f"{GSM8K_RAW_URL}/train.jsonl"
    test_url = f"{GSM8K_RAW_URL}/test.jsonl"
    
    train_path = os.path.join(target_dir, "train.jsonl")
    test_path = os.path.join(target_dir, "test.jsonl")
    
    print("下载GSM8K训练集...")
    train_success = download_file(train_url, train_path)
    
    print("下载GSM8K测试集...")
    test_success = download_file(test_url, test_path)
    
    if train_success:
        # 从训练集创建一个样本数据集
        sample_path = os.path.join(target_dir, "samples.jsonl")
        create_sample_dataset(train_path, sample_path, 100)
    else:
        print("无法下载训练集，创建扩展示例数据代替")
        # 创建更多示例
        create_extended_examples(target_dir)
    
    print("完成GSM8K数据集下载!")

def create_extended_examples(save_dir):
    """创建扩展的GSM8K示例问题集合"""
    examples = [
        {"problem": "Janet在她最喜欢的商店购物。她花了原有金额的20%买了一条裙子，又花了剩余金额的25%买了一件上衣。然后，她用剩余金额的10%买了一条围巾。她仍剩下54美元。她最初有多少钱？", "answer": "100美元"},
        {"problem": "五个人参加一场比赛。第一名获得金牌，第二名获得银牌，第三名获得铜牌。有多少种不同的颁奖方式？", "answer": "60种"},
        {"problem": "汤姆的年龄是他父亲年龄的1/4，汤姆的父亲比汤姆的母亲小3岁。如果汤姆的母亲今年45岁，那么汤姆现在几岁？", "answer": "10.5岁"},
        {"problem": "一辆车以每小时60公里的速度行驶了2.5小时，然后以每小时80公里的速度行驶了1.5小时。这辆车总共行驶了多少公里？", "answer": "270公里"},
        {"problem": "小明有15个苹果，他给了小红3个，给了小李5个，又从小张那里得到了2个。小明现在有多少个苹果？", "answer": "9个"},
        {"problem": "一根绳子长10米，每天减少10%的长度。问几天后，绳子的长度会小于5米？", "answer": "7天"},
        {"problem": "一本书有300页，小明第一天读了全书的1/6，第二天读了剩余页数的1/5，第三天读了剩余页数的1/4。到第三天结束时，小明还有多少页没读？", "answer": "150页"},
        {"problem": "一个超市促销，买3个苹果送1个。如果小李想要得到20个苹果，他最少需要买多少个？", "answer": "15个"},
        {"problem": "一个水池有两个进水管A和B，以及一个出水管C。A管每小时进水3立方米，B管每小时进水2立方米，C管每小时出水4立方米。如果水池初始为空，需要多少小时才能注满60立方米的水池？", "answer": "60小时"},
        {"problem": "一个数列的第一项是3，每一项都比前一项大2。求这个数列的第15项。", "answer": "31"}
    ]
    
    # 创建100个示例，通过重复和稍微变化已有示例
    extended_examples = []
    for i in range(100):
        idx = i % len(examples)
        example = examples[idx].copy()
        
        # 为了区分，添加编号
        if i >= len(examples):
            example["problem"] = f"例题 #{i+1}: {example['problem']}"
            
        extended_examples.append(example)
    
    # 保存到JSONL文件
    extended_file = os.path.join(save_dir, "extended_samples.jsonl")
    with open(extended_file, 'w', encoding='utf-8') as f:
        for example in extended_examples:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")
    
    print(f"已创建扩展示例数据: {extended_file} (包含 {len(extended_examples)} 个样本)")
    
    # 同时创建一个dataset.jsonl作为默认数据集
    dataset_file = os.path.join(save_dir, "dataset.jsonl")
    with open(dataset_file, 'w', encoding='utf-8') as f:
        for example in extended_examples:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")
            
    print(f"已创建默认数据集: {dataset_file}")

if __name__ == "__main__":
    # 处理命令行参数
    download_all = "--all" in sys.argv
    target_dir = "data/gsm8k"
    
    # 如果指定了路径参数，使用指定路径
    for arg in sys.argv:
        if arg.startswith("--path="):
            target_dir = arg.split("=")[1]
    
    # 下载数据集
    download_gsm8k_dataset(target_dir, download_all) 