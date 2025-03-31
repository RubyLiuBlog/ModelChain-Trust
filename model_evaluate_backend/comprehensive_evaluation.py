#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
全面评测脚本 - 参考OpenCompass的评测流程
支持同时对多个数据集(GSM8K, MATH)进行评测
"""

import os
import sys
import json
import argparse
import time
from datetime import datetime
import torch

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置离线环境变量
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"

from model_evaluate_demo.api import evaluate_model, list_datasets, list_metrics

def run_comprehensive_evaluation(model_path, output_dir="./outputs", datasets=None, 
                               max_samples=None, device=None, debug=False):
    """
    运行全面评测流程
    
    Args:
        model_path: 模型路径
        output_dir: 评测结果输出目录
        datasets: 要评测的数据集列表，如果为None则评测所有可用的数据集
        max_samples: 每个数据集使用的最大样本数量
        device: 使用的设备(cuda/cpu)
        debug: 是否开启调试模式
    """
    
    # 检查模型路径
    if not os.path.exists(model_path):
        print(f"错误: 模型路径不存在: {model_path}")
        return
        
    # 获取可用数据集
    available_datasets = list_datasets()
    if not datasets:
        datasets = available_datasets
    else:
        datasets = [d for d in datasets if d in available_datasets]
        
    if not datasets:
        print("错误: 没有可用的数据集进行评测")
        return
        
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    eval_id = f"{timestamp}_{os.path.basename(model_path)}"
    
    # 记录评测信息
    eval_info = {
        "model_path": model_path,
        "datasets": datasets,
        "timestamp": timestamp,
        "results": {}
    }
    
    # 确定使用设备
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # 获取设备信息
    if device == "cuda":
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        eval_info["hardware"] = {
            "device": device,
            "gpu_name": gpu_name,
            "gpu_memory_gb": f"{gpu_memory:.2f}"
        }
    else:
        eval_info["hardware"] = {"device": "cpu"}
    
    # 获取transformers版本
    import importlib
    transformers_version = importlib.import_module('transformers').__version__
    eval_info["environment"] = {"transformers_version": transformers_version}
    
    print(f"开始全面评测 - 模型: {model_path}")
    print(f"评测ID: {eval_id}")
    print(f"设备: {device}")
    print(f"将评测以下数据集: {', '.join(datasets)}")
    
    # 配置每个数据集的评测参数
    dataset_configs = {
        "gsm8k": {
            "max_samples": 100 if max_samples is None else max_samples,
            "metrics": ["accuracy"],
            "generation": {
                "temperature": 0.1,
                "max_tokens": 512,
                "num_beams": 1
            },
            "prompt_template": "问题: {{question}}\n请一步步思考并给出答案。"
        },
        "math": {
            "max_samples": 50 if max_samples is None else max_samples,
            "metrics": ["accuracy"],
            "generation": {
                "temperature": 0.1,
                "max_tokens": 1024,
                "num_beams": 1
            },
            "prompt_template": "问题: {{problem}}\n请仔细分析并逐步解答这个数学问题。确保你的推导过程清晰，并在最后明确给出答案。"
        }
    }
    
    # 运行每个数据集的评测
    total_start_time = time.time()
    
    for dataset in datasets:
        # 获取数据集配置，如果没有则使用默认值
        config = dataset_configs.get(dataset, {
            "max_samples": 50 if max_samples is None else max_samples,
            "metrics": ["accuracy"],
            "generation": {"temperature": 0.1, "max_tokens": 512}
        })
        
        print(f"\n=============== 评测数据集: {dataset} ===============")
        print(f"样本数量: {config['max_samples']}")
        
        # 如果max_samples是字典类型，则优先使用字典中对应数据集的样本数
        if isinstance(max_samples, dict) and dataset in max_samples:
            config["max_samples"] = max_samples[dataset]
            print(f"使用自定义样本数: {config['max_samples']}")
            
        start_time = time.time()
        try:
            results = evaluate_model(
                model_path=model_path,
                model_type="huggingface",
                dataset_name=dataset,
                metrics=config["metrics"],
                max_samples=config["max_samples"],
                offline=True,
                trust_remote_code=True,
                local_files_only=True,
                device=device,
                debug=debug,
                prompt_template=config.get("prompt_template"),
                generation_params=config.get("generation", {})
            )
            
            eval_time = time.time() - start_time
            
            # 记录结果
            eval_info["results"][dataset] = {
                "metrics": results["metrics"],
                "elapsed_time": f"{eval_time:.2f}秒",
                "sample_count": config["max_samples"]
            }
            
            # 保存每个样本的详细信息
            eval_info["results"][dataset]["samples"] = []
            for i, sample in enumerate(results["samples"]):
                is_correct = results["metrics"]["accuracy"]["details"][i]["correct"]
                
                # 保存关键信息
                eval_info["results"][dataset]["samples"].append({
                    "problem": sample.get("prompt", ""),
                    "prediction": sample.get("prediction", ""),
                    "reference": sample.get("reference", ""),
                    "extracted_prediction": results["metrics"]["accuracy"]["details"][i].get("extracted", ""),
                    "is_correct": is_correct
                })
            
            print(f"评测完成 - {dataset}:")
            print(f"准确率: {results['metrics']['accuracy']['score']:.4f}")
            print(f"正确: {results['metrics']['accuracy']['correct']}/{results['metrics']['accuracy']['total']}")
            print(f"耗时: {eval_time:.2f}秒")
            
        except Exception as e:
            print(f"评测失败 - {dataset}: {str(e)}")
            import traceback
            traceback.print_exc()
            eval_info["results"][dataset] = {
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    total_eval_time = time.time() - total_start_time
    eval_info["total_elapsed_time"] = f"{total_eval_time:.2f}秒"
    
    # 保存评测结果
    results_file = os.path.join(output_dir, f"{eval_id}_results.json")
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(eval_info, f, ensure_ascii=False, indent=2)
    
    # 同时创建一个summary文件
    summary_file = os.path.join(output_dir, f"{eval_id}_summary.json")
    summary = {
        "model": model_path,
        "timestamp": timestamp,
        "datasets": {}
    }
    
    # 计算综合得分
    overall_scores = {}
    for dataset, result in eval_info["results"].items():
        if "metrics" in result:
            metrics = result["metrics"]
            summary["datasets"][dataset] = {
                "accuracy": metrics["accuracy"]["score"],
                "correct": metrics["accuracy"]["correct"],
                "total": metrics["accuracy"]["total"]
            }
            
            for metric_name, metric_result in metrics.items():
                if isinstance(metric_result, dict) and "score" in metric_result:
                    if metric_name not in overall_scores:
                        overall_scores[metric_name] = []
                    overall_scores[metric_name].append(metric_result["score"])
    
    # 计算平均分
    if overall_scores:
        summary["overall"] = {}
        for metric_name, scores in overall_scores.items():
            avg_score = sum(scores) / len(scores)
            summary["overall"][metric_name] = avg_score
    
    # 保存摘要
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print("\n=============== 评测全部完成! ===============")
    print(f"总耗时: {total_eval_time:.2f}秒")
    print(f"结果已保存到: {results_file}")
    print(f"摘要已保存到: {summary_file}")
    
    # 打印综合得分
    if overall_scores:
        print("\n综合评测得分:")
        for metric_name, scores in overall_scores.items():
            avg_score = sum(scores) / len(scores)
            print(f"{metric_name}: {avg_score:.4f}")
    
    return eval_info

def main():
    parser = argparse.ArgumentParser(description="模型综合评测脚本")
    parser.add_argument("--model-path", type=str, default="/home/bugsmith/qwen",
                      help="模型路径")
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
    run_comprehensive_evaluation(
        args.model_path, 
        args.output_dir, 
        args.datasets, 
        args.max_samples,
        args.device,
        args.debug
    )

if __name__ == "__main__":
    main() 