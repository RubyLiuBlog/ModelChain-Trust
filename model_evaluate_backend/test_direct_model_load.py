#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
直接使用transformers库测试模型加载
"""

import os
import sys

# 设置离线环境变量
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"

def test_model_loading(model_path):
    """测试模型是否可以成功加载"""
    try:
        print(f"开始测试加载模型: {model_path}")
        print("1. 导入必要库...")
        from transformers import AutoTokenizer, AutoModelForCausalLM
        import torch
        
        print(f"2. 检查GPU可用性...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"   使用设备: {device}")
        if device == "cuda":
            print(f"   GPU: {torch.cuda.get_device_name(0)}")
            print(f"   可用内存: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB")
            print(f"   当前内存使用: {torch.cuda.memory_allocated() / (1024**3):.2f} GB")
        
        print(f"3. 尝试加载tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            local_files_only=True,
            trust_remote_code=True
        )
        print(f"   Tokenizer成功加载: {type(tokenizer).__name__}")
        
        print(f"4. 尝试加载模型...")
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            local_files_only=True,
            trust_remote_code=True,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            low_cpu_mem_usage=True,
            device_map="auto" if device == "cuda" else None
        )
        print(f"   模型成功加载: {type(model).__name__}")
        
        print(f"5. 尝试简单推理...")
        input_text = "2 + 2 = "
        input_ids = tokenizer(input_text, return_tensors="pt").to(device)
        
        with torch.no_grad():
            output = model.generate(
                **input_ids,
                max_new_tokens=20,
                do_sample=False,
                temperature=0.0
            )
        
        result = tokenizer.decode(output[0], skip_special_tokens=True)
        print(f"   输入: {input_text}")
        print(f"   输出: {result}")
        
        print("测试完成! 模型可以正常加载和使用。")
        return True
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 默认使用qwen目录
    model_path = "/home/bugsmith/qwen"
    
    # 允许从命令行指定模型路径
    if len(sys.argv) > 1:
        model_path = sys.argv[1]
    
    print(f"使用模型路径: {model_path}")
    if not os.path.exists(model_path):
        print(f"错误: 路径不存在: {model_path}")
        sys.exit(1)
    
    # 测试模型加载
    success = test_model_loading(model_path)
    sys.exit(0 if success else 1) 