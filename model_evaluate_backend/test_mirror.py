#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
使用镜像站点测试模型加载
"""

import os
import sys

# 设置HuggingFace镜像站点
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入模型
from model_evaluate_demo.models.huggingface import HuggingFaceModel

def main():
    # 模型路径
    model_path = "/home/bugsmith/model_evaluate_demo/models/qwen_local"
    
    # 检查路径是否存在
    if not os.path.exists(model_path):
        print(f"错误: 模型路径不存在 {model_path}")
        return
    
    print(f"测试加载模型: {model_path}")
    print(f"模型目录内容: {os.listdir(model_path)}")
    
    # 创建模型实例
    model = HuggingFaceModel(
        model_name=model_path,
        trust_remote_code=True,
        device="cuda",
        offline=True
    )
    
    try:
        # 加载模型
        print("开始加载模型...")
        model.load()
        
        # 测试生成
        prompt = "Solve this step-by-step:\nProblem: What is 2+2?"
        print(f"\n测试生成，提示: {prompt}")
        
        response = model.generate([prompt], 
                                  temperature=0.0, 
                                  max_new_tokens=256, 
                                  do_sample=False)
        
        print(f"\n生成结果: {response[0]}")
        print("\n测试完成!")
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 