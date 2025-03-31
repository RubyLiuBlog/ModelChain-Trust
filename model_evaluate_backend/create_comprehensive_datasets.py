#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
创建更大规模的GSM8K和MATH数据集用于全面评测
参考OpenCompass的评测标准和数据规模
"""

import os
import sys
import json
import random
import argparse
from tqdm import tqdm

# GSM8K示例问题
GSM8K_EXAMPLES = [
    {
        "problem": "Janet在她最喜欢的商店购物。她花了原有金额的20%买了一条裙子，又花了剩余金额的25%买了一件上衣。然后，她用剩余金额的10%买了一条围巾。她仍剩下54美元。她最初有多少钱？",
        "answer": "100美元"
    },
    {
        "problem": "五个人参加一场比赛。第一名获得金牌，第二名获得银牌，第三名获得铜牌。有多少种不同的颁奖方式？",
        "answer": "60种"
    },
    {
        "problem": "汤姆的年龄是他父亲年龄的1/4，汤姆的父亲比汤姆的母亲小3岁。如果汤姆的母亲今年45岁，那么汤姆现在几岁？",
        "answer": "10.5岁"
    },
    {
        "problem": "一辆车以每小时60公里的速度行驶了2.5小时，然后以每小时80公里的速度行驶了1.5小时。这辆车总共行驶了多少公里？",
        "answer": "270公里"
    },
    {
        "problem": "小明有15个苹果，他给了小红3个，给了小李5个，又从小张那里得到了2个。小明现在有多少个苹果？",
        "answer": "9个"
    },
    {
        "problem": "一根绳子长10米，每天减少10%的长度。问几天后，绳子的长度会小于5米？",
        "answer": "7天"
    },
    {
        "problem": "一本书有300页，小明第一天读了全书的1/6，第二天读了剩余页数的1/5，第三天读了剩余页数的1/4。到第三天结束时，小明还有多少页没读？",
        "answer": "150页"
    },
    {
        "problem": "一个超市促销，买3个苹果送1个。如果小李想要得到20个苹果，他最少需要买多少个？",
        "answer": "15个"
    },
    {
        "problem": "一个水池有两个进水管A和B，以及一个出水管C。A管每小时进水3立方米，B管每小时进水2立方米，C管每小时出水4立方米。如果水池初始为空，需要多少小时才能注满60立方米的水池？",
        "answer": "60小时"
    },
    {
        "problem": "一个数列的第一项是3，每一项都比前一项大2。求这个数列的第15项。",
        "answer": "31"
    }
]

# MATH示例问题
MATH_EXAMPLES = [
    {
        "problem": "假设集合S是{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}的子集，满足以下条件：a) 如果x在S中，那么x+2也在S中，如果x+2 ≤ 10；b) 集合S中恰好有7个元素。求所有可能的集合S的数量。",
        "answer": "4",
        "type": "number_theory",
        "level": "Level 3"
    },
    {
        "problem": "解方程：x^4 - 13x^2 + 36 = 0。",
        "answer": "x = -3, x = -2, x = 2, x = 3",
        "type": "algebra",
        "level": "Level 2"
    },
    {
        "problem": "一个圆的半径为5，求该圆的面积。",
        "answer": "25π",
        "type": "geometry",
        "level": "Level 1"
    },
    {
        "problem": "计算：∫(0到π/2) sin(x)dx",
        "answer": "1",
        "type": "precalculus",
        "level": "Level 2"
    },
    {
        "problem": "如果P(A) = 0.3，P(B) = 0.4，且A和B是互斥事件，求P(A或B)。",
        "answer": "0.7",
        "type": "counting_and_probability",
        "level": "Level 1"
    },
    {
        "problem": "求函数f(x) = 3x^3 - 6x^2 + 2的导数。",
        "answer": "f'(x) = 9x^2 - 12x",
        "type": "precalculus",
        "level": "Level 2"
    },
    {
        "problem": "一个等差数列的首项为3，公差为4，求该数列的第20项。",
        "answer": "79",
        "type": "algebra",
        "level": "Level 1"
    },
    {
        "problem": "在△ABC中，已知角A = 30°，角B = 45°，边BC = 10。求边AB的长度。",
        "answer": "7.66",
        "type": "geometry",
        "level": "Level 2"
    },
    {
        "problem": "求复数z = 3 + 4i的模。",
        "answer": "5",
        "type": "algebra",
        "level": "Level 2"
    },
    {
        "problem": "方程x^2 + y^2 - 6x + 8y + 25 = 0表示什么几何图形？给出该图形的基本特征。",
        "answer": "圆，圆心(3, -4)，半径为2",
        "type": "geometry",
        "level": "Level 2"
    }
]

def create_variants(examples, n_variants=10):
    """为每个基本示例创建多个变体"""
    all_examples = []
    for example in examples:
        all_examples.append(example)  # 添加原始示例
        
        base_problem = example["problem"]
        base_answer = example["answer"]
        
        # 根据问题类型确定变量替换方式
        num_pattern = r'\d+'
        numbers = list(map(int, re.findall(num_pattern, base_problem)))
        
        for i in range(n_variants):
            if not numbers:
                continue  # 如果没有数字可替换，跳过
                
            # 创建问题变体
            new_problem = base_problem
            new_answer = base_answer
            
            # 随机替换数字（简单变换）
            for num in numbers:
                # 在原数字基础上增加或减少一个小的随机值
                change = random.randint(1, 5)
                new_num = num + change if random.random() > 0.5 else num - change
                
                # 确保新数字为正
                if new_num <= 0:
                    new_num = num + change
                
                # 替换问题中的数字
                new_problem = new_problem.replace(str(num), str(new_num), 1)
                
                # 尝试调整答案（这是一个简化处理，实际情况可能需要更复杂的逻辑）
                if str(num) in new_answer:
                    new_answer = new_answer.replace(str(num), str(new_num), 1)
            
            # 添加变体到列表
            variant = example.copy()
            variant["problem"] = f"例题 #{len(all_examples) + 1}: {new_problem}"
            variant["answer"] = new_answer
            
            all_examples.append(variant)
            
            # 如果已经生成足够的变体，就停止
            if len(all_examples) >= n_variants:
                break
    
    return all_examples

def create_dataset(examples, output_path, n_samples=100):
    """创建示例数据集"""
    # 确保目标目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 如果样本数超过示例数，则通过复制和轻微修改创建更多样本
    if n_samples > len(examples):
        # 首先复制到达到需要的数量
        samples = []
        
        # 循环复制示例，直到达到所需数量
        for i in range(n_samples):
            idx = i % len(examples)
            sample = examples[idx].copy()
            
            # 为了区分，添加编号
            if i >= len(examples):
                sample["problem"] = f"例题 #{i+1}: {sample['problem']}"
                
            samples.append(sample)
    else:
        # 取前n_samples个样本
        samples = examples[:n_samples]
    
    # 写入到JSONL文件
    with open(output_path, 'w', encoding='utf-8') as f:
        for sample in samples:
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')
    
    print(f"已创建包含 {len(samples)} 个样本的数据集: {output_path}")
    return len(samples)

def main():
    parser = argparse.ArgumentParser(description="创建大规模评测数据集")
    parser.add_argument("--output-dir", type=str, default="./data",
                      help="数据集输出目录")
    parser.add_argument("--gsm8k-samples", type=int, default=100,
                      help="GSM8K数据集样本数")
    parser.add_argument("--math-samples", type=int, default=50,
                      help="MATH数据集样本数")
    parser.add_argument("--force", action="store_true", 
                      help="强制覆盖现有文件")
    
    args = parser.parse_args()
    
    # 导入re模块（用于变体创建）
    import re
    
    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)
    
    # GSM8K数据集路径
    gsm8k_dir = os.path.join(args.output_dir, "gsm8k")
    os.makedirs(gsm8k_dir, exist_ok=True)
    gsm8k_path = os.path.join(gsm8k_dir, "dataset.jsonl")
    
    # MATH数据集路径
    math_dir = os.path.join(args.output_dir, "math")
    os.makedirs(math_dir, exist_ok=True)
    math_path = os.path.join(math_dir, "dataset.jsonl")
    
    # 创建GSM8K数据集
    if not os.path.exists(gsm8k_path) or args.force:
        print(f"创建GSM8K数据集 ({args.gsm8k_samples} 样本)...")
        # 为基本示例创建变体以增加数据量
        if args.gsm8k_samples > len(GSM8K_EXAMPLES):
            expanded_gsm8k = GSM8K_EXAMPLES * (args.gsm8k_samples // len(GSM8K_EXAMPLES) + 1)
            expanded_gsm8k = expanded_gsm8k[:args.gsm8k_samples]
        else:
            expanded_gsm8k = GSM8K_EXAMPLES[:args.gsm8k_samples]
            
        samples_created = create_dataset(expanded_gsm8k, gsm8k_path, args.gsm8k_samples)
        print(f"GSM8K数据集创建完成，共 {samples_created} 个样本")
    else:
        print(f"GSM8K数据集已存在: {gsm8k_path}")
    
    # 创建MATH数据集
    if not os.path.exists(math_path) or args.force:
        print(f"创建MATH数据集 ({args.math_samples} 样本)...")
        # 为基本示例创建变体以增加数据量
        if args.math_samples > len(MATH_EXAMPLES):
            expanded_math = MATH_EXAMPLES * (args.math_samples // len(MATH_EXAMPLES) + 1)
            expanded_math = expanded_math[:args.math_samples]
        else:
            expanded_math = MATH_EXAMPLES[:args.math_samples]
            
        samples_created = create_dataset(expanded_math, math_path, args.math_samples)
        print(f"MATH数据集创建完成，共 {samples_created} 个样本")
    else:
        print(f"MATH数据集已存在: {math_path}")

if __name__ == "__main__":
    main() 