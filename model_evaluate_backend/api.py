#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
模型评测框架API接口
"""

import os
import sys
import time
import json
import logging
import datetime
from typing import List, Dict, Any, Optional, Union

# 设置HuggingFace镜像站点
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# 使用相对导入
from model_evaluate_demo.tasks import TaskRunner
from model_evaluate_demo.utils.registry import MODELS, DATASETS, METRICS

def get_available_datasets() -> List[str]:
    """
    获取所有可用的数据集列表
    
    Returns:
        List[str]: 可用数据集名称列表
    """
    return sorted(DATASETS.list())

def get_available_metrics() -> List[str]:
    """
    获取所有可用的评估指标列表
    
    Returns:
        List[str]: 可用评估指标名称列表
    """
    return sorted(METRICS.list())

def get_available_model_types() -> List[str]:
    """
    获取所有可用的模型类型列表
    
    Returns:
        List[str]: 可用模型类型名称列表
    """
    return sorted(MODELS.list())

def get_default_generation_params() -> Dict[str, Any]:
    """
    获取默认的生成参数
    
    Returns:
        Dict[str, Any]: 默认生成参数字典
    """
    return {
        'max_tokens': 256,        # 最大生成token数
        'temperature': 0.7,       # 温度参数
        'top_p': 0.9,             # top-p采样参数
        'repetition_penalty': 1.0,  # 重复惩罚参数
        'do_sample': True,        # 是否使用采样
    }

def evaluate_model(
    model_path: str,
    model_type: str = "huggingface",
    dataset_name: str = "math",
    dataset_path: Optional[str] = None,
    metrics: List[str] = ["accuracy"],
    max_samples: Optional[int] = None,
    batch_size: int = 1,
    output_dir: str = "./outputs",
    debug: bool = False,
    temperature: float = 0.7,
    max_tokens: int = 256,
    system_message: Optional[str] = None,
    prompt_template: Optional[str] = None,
    retry_count: int = 0,
    offline: bool = False,
    local_files_only: bool = False,
    trust_remote_code: bool = False,
    device: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    评测模型API
    
    Args:
        model_path: 模型路径或名称
        model_type: 模型类型，如"huggingface"或"openai"
        dataset_name: 数据集名称
        dataset_path: 数据集路径，如果提供则优先使用
        metrics: 评估指标列表
        max_samples: 最大评估样本数，None表示使用全部样本
        batch_size: 批处理大小
        output_dir: 输出目录
        debug: 是否启用调试模式
        temperature: 生成温度
        max_tokens: 最大生成token数
        system_message: 系统消息(对于支持系统消息的模型)
        prompt_template: 提示模板
        retry_count: API调用失败时的重试次数
        offline: 是否使用离线模式
        local_files_only: 是否只使用本地文件
        trust_remote_code: 是否信任远程代码
        device: 设备类型，如"cuda"或"cpu"
        **kwargs: 其他参数
        
    Returns:
        Dict[str, Any]: 评测结果
    """
    logger.info(f"开始评测模型: {model_path}")
    logger.info(f"模型类型: {model_type}, 数据集: {dataset_name}")
    
    # 参数检查
    if model_type not in MODELS:
        raise ValueError(f"不支持的模型类型: {model_type}。支持的类型: {', '.join(MODELS.keys())}")
    
    if dataset_name not in DATASETS:
        raise ValueError(f"不支持的数据集: {dataset_name}。支持的数据集: {', '.join(DATASETS.keys())}")
    
    for metric in metrics:
        if metric not in METRICS:
            raise ValueError(f"不支持的评估指标: {metric}。支持的指标: {', '.join(METRICS.keys())}")
    
    # 生成任务配置
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    task_name = f"{model_type}_{dataset_name}_eval_{timestamp}"
    
    # 准备模型配置
    model_config = {
        "name": model_type,
        "model_name": model_path,  # 确保使用model_path
        "retry_count": retry_count
    }
    
    # 添加HuggingFace特定参数
    if model_type == "huggingface":
        model_config.update({
            "offline": offline,
            "local_files_only": local_files_only,
            "trust_remote_code": trust_remote_code,
            "load_8bit": kwargs.get("load_8bit", False),
            "load_4bit": kwargs.get("load_4bit", False)
        })
        
        if device:
            model_config["device"] = device
    
    # 准备数据集配置
    dataset_config = {
        "name": dataset_name
    }
    
    # 如果提供了数据集路径，添加到配置中
    if dataset_path:
        dataset_config["data_path"] = dataset_path
    
    if max_samples is not None:
        dataset_config["max_samples"] = max_samples
    
    # 准备评测配置
    eval_config = {
        "batch_size": batch_size,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    # 添加可选配置
    if system_message:
        eval_config["system_message"] = system_message
        
    if prompt_template:
        eval_config["prompt_template"] = prompt_template
    
    # 添加其他kwargs参数到适当的配置中
    for k, v in kwargs.items():
        if k.startswith("model_"):
            # 模型相关参数
            model_config[k[6:]] = v
        elif k.startswith("dataset_"):
            # 数据集相关参数
            dataset_config[k[9:]] = v
        elif k.startswith("eval_"):
            # 评测相关参数
            eval_config[k[5:]] = v
    
    # 构建完整任务配置
    task_config = {
        "name": task_name,
        "model": model_config,
        "dataset": dataset_config,
        "metrics": metrics,
        "eval_config": eval_config
    }
    
    # 构建配置字典
    config = {
        "global": {
            "output_dir": output_dir,
            "debug": debug
        },
        "tasks": [task_config]
    }
    
    # 创建TaskRunner并执行评测
    logger.info("开始运行评测...")
    runner = TaskRunner(output_dir=output_dir, debug=debug)
    results = runner.run_from_dict(config)
    
    # 处理结果
    task_result = results['tasks'][0] if results.get('tasks') else {}
    
    # 保存API调用结果
    os.makedirs(output_dir, exist_ok=True)
    result_file = os.path.join(output_dir, f"{timestamp}_api_result_{task_name}.json")
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(task_result, f, ensure_ascii=False, indent=2)
    logger.info(f"API评测结果已保存到: {result_file}")
    
    return task_result

def save_results(results, output_dir):
    """保存评测结果到JSON文件"""
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成文件名
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{timestamp}_api_result_{results.get('task_name', 'unknown')}.json"
    filepath = os.path.join(output_dir, filename)
    
    # 保存为JSON文件
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    logger.info(f"API评测结果已保存到: {filepath}")
    
def list_available_datasets():
    """返回可用的数据集列表"""
    from model_evaluate_demo.utils.registry import DATASETS
    return DATASETS.list()

def list_available_metrics():
    """返回可用的评估指标列表"""
    from model_evaluate_demo.utils.registry import METRICS
    return METRICS.list()

def list_available_model_types():
    """返回可用的模型类型列表"""
    from model_evaluate_demo.utils.registry import MODELS
    return MODELS.list()

def get_default_generation_kwargs():
    """返回默认的生成参数，兼容旧版接口"""
    return get_default_generation_params()

# 添加别名函数，兼容comprehensive_evaluation脚本
list_datasets = get_available_datasets
list_metrics = get_available_metrics
list_model_types = get_available_model_types 