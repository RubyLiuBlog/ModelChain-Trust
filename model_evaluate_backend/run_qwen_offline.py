#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
运行Qwen模型评估（离线模式）
"""

import os
import sys
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 使用绝对导入
from model_evaluate_demo.tasks import TaskRunner

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    # 配置文件路径
    config_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 
        "configs", 
        "qwen_offline.yaml"
    )
    
    # 检查配置文件是否存在
    if not os.path.exists(config_path):
        logger.error(f"配置文件不存在: {config_path}")
        return
    
    logger.info(f"加载配置文件: {config_path}")
    
    try:
        # 初始化任务运行器
        logger.info("初始化任务运行器...")
        runner = TaskRunner(
            config_path=config_path,
            output_dir="./outputs",
            debug=True
        )
        
        # 运行评估
        logger.info("开始评估...")
        results = runner.run_from_config()
        
        logger.info("评估完成")
        return results
    
    except Exception as e:
        logger.exception(f"评估过程中出错: {str(e)}")
        return None

if __name__ == "__main__":
    main() 