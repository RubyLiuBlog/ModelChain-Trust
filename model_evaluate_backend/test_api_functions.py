#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试API功能是否可用
"""

import os
import sys

# 设置HuggingFace镜像站点
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_list_functions():
    """测试列表函数是否可用"""
    try:
        from model_evaluate_demo.api import (
            list_available_datasets, 
            list_available_metrics, 
            list_available_model_types
        )
        
        print("测试列出可用数据集...")
        datasets = list_available_datasets()
        print(f"可用数据集: {datasets}")
        
        print("\n测试列出可用评估指标...")
        metrics = list_available_metrics()
        print(f"可用评估指标: {metrics}")
        
        print("\n测试列出可用模型类型...")
        model_types = list_available_model_types()
        print(f"可用模型类型: {model_types}")
        
        print("\n所有列表功能测试通过!")
        return True
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_default_kwargs():
    """测试获取默认生成参数是否可用"""
    try:
        from model_evaluate_demo.api import get_default_generation_kwargs
        
        print("测试获取默认生成参数...")
        kwargs = get_default_generation_kwargs()
        print(f"默认生成参数: {kwargs}")
        
        print("默认生成参数功能测试通过!")
        return True
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始测试API功能...\n")
    
    # 测试列表功能
    list_test_passed = test_list_functions()
    
    # 测试默认参数功能
    kwargs_test_passed = test_default_kwargs()
    
    # 总结测试结果
    if list_test_passed and kwargs_test_passed:
        print("\n所有测试通过! API功能正常。")
        return 0
    else:
        print("\n测试失败! 请检查错误信息。")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 