#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
模型评测系统主运行脚本
"""
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 使用绝对导入
from model_evaluate_demo.utils.registry import MODELS, DATASETS, METRICS
from model_evaluate_demo.tasks import TaskRunner


def main():
    """
    主函数
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='模型评测系统')
    parser.add_argument('config', nargs='?', type=str, help='配置文件路径')
    parser.add_argument('--model', type=str, help='模型名称')
    parser.add_argument('--model-name', type=str, help='具体模型名称，如gpt-3.5-turbo')
    parser.add_argument('--dataset', type=str, help='数据集名称')
    parser.add_argument('--metric', type=str, default='accuracy', help='评估指标名称')
    parser.add_argument('--output-dir', type=str, default='outputs', help='输出目录')
    parser.add_argument('--max-samples', type=int, help='最大样本数')
    parser.add_argument('--debug', action='store_true', help='开启调试模式')
    parser.add_argument('--list-models', action='store_true', help='列出所有已注册的模型')
    parser.add_argument('--list-datasets', action='store_true', help='列出所有已注册的数据集')
    parser.add_argument('--list-metrics', action='store_true', help='列出所有已注册的评估指标')
    
    args = parser.parse_args()
    
    # 显示已注册的组件
    if args.list_models:
        print("已注册的模型:")
        for name in MODELS.list():
            print(f"  - {name}")
        return
        
    if args.list_datasets:
        print("已注册的数据集:")
        for name in DATASETS.list():
            print(f"  - {name}")
        return
        
    if args.list_metrics:
        print("已注册的评估指标:")
        for name in METRICS.list():
            print(f"  - {name}")
        return
    
    # 从配置文件运行
    if args.config:
        if not os.path.exists(args.config):
            print(f"错误: 配置文件不存在: {args.config}")
            return 1
            
        print(f"从配置文件 {args.config} 加载任务")
        runner = TaskRunner(
            config_path=args.config,
            output_dir=args.output_dir,
            debug=args.debug
        )
        runner.run_from_config()
        return 0
    
    # 使用命令行参数运行
    if args.model and args.dataset:
        from model_evaluate_demo.tasks.evaluator import Evaluator
        
        print(f"使用模型 {args.model} 评测数据集 {args.dataset}")
        
        # 构建配置字典
        model_config = {
            'name': args.model
        }
        
        # 添加模型名称参数（如果提供）
        if args.model_name:
            if args.model == 'openai':
                model_config['model_name'] = args.model_name
            else:
                # 对于其他模型类型，使用model_name参数
                model_config['model_name'] = args.model_name
        elif args.model == 'openai':
            # OpenAI模型需要默认的模型名称
            model_config['model_name'] = 'gpt-3.5-turbo'
        
        config = {
            'tasks': [{
                'name': f"{args.model}_{args.dataset}_test",
                'model': model_config,
                'dataset': {
                    'name': args.dataset
                },
                'metrics': [args.metric],
                'eval_config': {}
            }]
        }
        
        if args.max_samples:
            config['tasks'][0]['dataset']['max_samples'] = args.max_samples
            
        # 创建输出目录
        os.makedirs(args.output_dir, exist_ok=True)
            
        runner = TaskRunner(
            output_dir=args.output_dir,
            debug=args.debug
        )
        runner.run_from_dict(config)
        return 0
    
    # 如果没有提供足够的参数，显示帮助信息
    parser.print_help()
    return 1


if __name__ == '__main__':
    sys.exit(main()) 