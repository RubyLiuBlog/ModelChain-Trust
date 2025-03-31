#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试评测MATH数据集，允许指定样本数量
"""

import sys
import os
import argparse

# 在导入任何transformers库前设置离线环境变量
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    # 命令行参数
    parser = argparse.ArgumentParser(description='评测模型在MATH数据集上的表现')
    parser.add_argument('--model-path', type=str, default="/home/bugsmith/qwen",
                       help='模型路径')
    parser.add_argument('--samples', type=int, default=3,
                       help='评测样本数量')
    parser.add_argument('--data-path', type=str, default=None,
                       help='MATH数据集路径')
    parser.add_argument('--device', type=str, default=None,
                       help='设备(cuda或cpu)')
    args = parser.parse_args()
    
    # 检查模型路径
    if not os.path.exists(args.model_path):
        print(f"错误: 模型路径不存在: {args.model_path}")
        return 1
    
    print(f"模型路径: {args.model_path}")
    print(f"评测样本数量: {args.samples}")
    
    # 导入必要模块
    import torch
    from model_evaluate_demo.api import evaluate_model
    
    # 获取当前transformers版本
    import importlib
    transformers_version = importlib.import_module('transformers').__version__
    print(f"当前使用的transformers版本: {transformers_version}")
    
    # 确定设备
    if args.device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    else:
        device = args.device
    
    # 评测模型
    try:
        print(f"\n开始评测模型: {args.model_path}...")
        results = evaluate_model(
            model_path=args.model_path,  # 使用本地模型路径
            model_type="huggingface",
            dataset_name="math", 
            dataset_path=args.data_path,  # 数据集路径
            metrics=["accuracy"],
            max_samples=args.samples,  # 指定样本数量
            offline=True,  # 确保离线模式
            trust_remote_code=True,  # Qwen模型通常需要trust_remote_code
            local_files_only=True,  # 确保只使用本地文件
            device=device,  # 自动检测设备
            debug=True  # 打开调试输出
        )
        
        # 返回结果给用户
        print("\n评测结果:")
        print(f"准确率: {results['metrics']['accuracy']['score']:.4f}")
        print(f"正确: {results['metrics']['accuracy']['correct']}/{results['metrics']['accuracy']['total']}")
        
        # 打印每个样本的结果
        print("\n样本详情:")
        for i, sample in enumerate(results['samples']):
            # 截断过长的文本
            max_len = 100
            prompt = sample['prompt']
            if len(prompt) > max_len:
                prompt = prompt[:max_len] + "..."
                
            prediction = sample.get('prediction', '')
            if len(prediction) > max_len:
                prediction = prediction[:max_len] + "..."
            
            print(f"Sample {i+1}:")
            print(f"  问题: {prompt}")
            print(f"  模型答案: {prediction}")
            print(f"  正确答案: {sample.get('reference', '未知')}")
            
            # 判断是否正确
            is_correct = results['metrics']['accuracy']['details'][i]['correct']
            print(f"  结果: {'✓ 正确' if is_correct else '✗ 错误'}")
            print()
        
        return 0
        
    except Exception as e:
        print(f"评测过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 