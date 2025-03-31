"""
模型评测系统 - 仿照OpenCompass的简化版实现
"""

__version__ = '0.1.0'

# 导入子模块确保所有组件被注册
from model_evaluate_demo.utils.registry import MODELS, DATASETS, METRICS

# 导入所有模型
from model_evaluate_demo.models import *

# 导入所有数据集
from model_evaluate_demo.datasets import *

# 导入所有评估指标
from model_evaluate_demo.metrics import * 