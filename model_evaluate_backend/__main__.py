#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
模型评测系统主模块执行脚本
"""
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入运行脚本并执行
from model_evaluate_demo.run import main

if __name__ == '__main__':
    sys.exit(main()) 