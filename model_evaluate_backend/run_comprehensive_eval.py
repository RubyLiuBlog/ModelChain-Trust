#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
运行全面评测 - 入口脚本
支持使用配置文件或命令行参数进行评测
"""

import os
import sys
import argparse
import yaml
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置离线环境变量
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"

from model_evaluate_demo.comprehensive_evaluation import run_comprehensive_evaluation

def main():
    parser = argparse.ArgumentParser(description="运行全面模型评测")
    
    # 配置文件或直接参数两种使用方式
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("--config", type=str, help="评测配置文件路径")
    mode_group.add_argument("--model-path", type=str, help="模型路径")
    
    # 其他可选参数
    parser.add_argument("--output-dir", type=str, default="./outputs", 
                      help="评测结果输出目录")
    parser.add_argument("--datasets", type=str, nargs="+",
                      help="要评测的数据集列表")
    parser.add_argument("--max-samples", type=int, default=None,
                      help="每个数据集使用的最大样本数量")
    parser.add_argument("--device", type=str, choices=["cuda", "cpu"], default=None,
                      help="使用的设备")
    parser.add_argument("--debug", action="store_true",
                      help="开启调试模式")
    
    args = parser.parse_args()
    
    # 检查数据集是否存在
    if args.datasets:
        for dataset in args.datasets:
            dataset_path = os.path.join("data", dataset, "dataset.jsonl")
            if not os.path.exists(dataset_path):
                print(f"警告: 数据集 {dataset} 不存在于 {dataset_path}")
                print(f"是否要下载或创建 {dataset} 数据集? (y/n)")
                response = input().strip().lower()
                if response == 'y':
                    # 下载或创建数据集
                    if dataset == "gsm8k":
                        from model_evaluate_demo.download_gsm8k_dataset import download_gsm8k_dataset
                        download_gsm8k_dataset(f"data/{dataset}")
                    elif dataset == "math":
                        from model_evaluate_demo.download_math_dataset import download_math_dataset
                        download_math_dataset(f"data/{dataset}")
                    else:
                        print(f"不支持自动下载数据集 {dataset}")
                        return 1
    
    # 使用配置文件
    if args.config:
        try:
            with open(args.config, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                
            # 从配置文件读取全局设置
            global_config = config.get('global', {})
            output_dir = args.output_dir or global_config.get('output_dir')
            debug = args.debug or global_config.get('debug', False)
            
            # 检查配置文件中的任务
            tasks = config.get('tasks', [])
            if not tasks:
                print("错误: 配置文件不包含任何任务")
                return 1
                
            # 获取所有模型和数据集评测组合
            model_dataset_pairs = []
            for task in tasks:
                model_config = task.get('model', {})
                dataset_config = task.get('dataset', {})
                
                model_path = model_config.get('path')
                if not model_path:
                    print(f"错误: 任务 {task.get('name')} 未指定模型路径")
                    continue
                    
                dataset_name = dataset_config.get('name')
                if not dataset_name:
                    print(f"错误: 任务 {task.get('name')} 未指定数据集")
                    continue
                
                max_samples = dataset_config.get('max_samples')
                
                model_dataset_pairs.append({
                    'model_path': model_path,
                    'dataset': dataset_name,
                    'max_samples': max_samples
                })
                
            # 按模型分组执行评测
            models = {}
            for pair in model_dataset_pairs:
                model_path = pair['model_path']
                if model_path not in models:
                    models[model_path] = []
                models[model_path].append({
                    'dataset': pair['dataset'],
                    'max_samples': pair['max_samples']
                })
                
            # 针对每个模型执行评测
            results = {}
            for model_path, datasets_info in models.items():
                print(f"\n============ 评测模型: {model_path} ============\n")
                
                # 提取所有要评测的数据集
                datasets = [d['dataset'] for d in datasets_info]
                
                # 找出数据集中最小的样本数
                samples_by_dataset = {}
                for d in datasets_info:
                    dataset = d['dataset']
                    samples = d['max_samples']
                    samples_by_dataset[dataset] = samples
                
                # 执行评测
                device = args.device or next((task['model'].get('device') for task in tasks 
                                          if task['model'].get('path') == model_path 
                                          and task['model'].get('device')), None)
                
                model_results = run_comprehensive_evaluation(
                    model_path=model_path,
                    output_dir=output_dir,
                    datasets=datasets,
                    max_samples=samples_by_dataset,
                    device=device,
                    debug=debug
                )
                
                results[model_path] = model_results
            
            return 0
                
        except Exception as e:
            print(f"配置文件处理失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return 1
    
    # 直接使用命令行参数
    else:
        if not args.model_path:
            print("错误: 未指定模型路径")
            return 1
            
        model_results = run_comprehensive_evaluation(
            model_path=args.model_path,
            output_dir=args.output_dir,
            datasets=args.datasets,
            max_samples=args.max_samples,
            device=args.device,
            debug=args.debug
        )
        
        return 0
    
if __name__ == "__main__":
    sys.exit(main()) 