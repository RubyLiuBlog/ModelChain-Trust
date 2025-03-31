#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
尝试用旧版transformers加载Qwen模型的简单测试
"""

import os
import sys
import torch
from transformers import AutoConfig, PreTrainedTokenizerFast, AutoModelForCausalLM

# 设置离线环境变量
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"

def test_model_with_fallback(model_path):
    """测试模型加载，尝试通用方法"""
    try:
        print(f"开始测试加载模型: {model_path}")
        print(f"1. 导入必要库完成")
        
        import transformers
        print(f"transformers版本: {transformers.__version__}")
        
        print(f"2. 检查GPU可用性...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"   使用设备: {device}")
        if device == "cuda":
            print(f"   GPU: {torch.cuda.get_device_name(0)}")
            print(f"   可用内存: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB")
            print(f"   当前内存使用: {torch.cuda.memory_allocated() / (1024**3):.2f} GB")
        
        # 检查模型目录
        print(f"3. 检查模型目录...")
        if not os.path.exists(model_path):
            print(f"   错误: 模型路径不存在: {model_path}")
            return False
        
        files = os.listdir(model_path)
        print(f"   目录包含 {len(files)} 个文件:")
        for file in files:
            file_size = os.path.getsize(os.path.join(model_path, file)) / (1024 * 1024)
            print(f"   - {file} ({file_size:.2f} MB)")
        
        # 尝试加载配置
        print(f"4. 尝试加载模型配置...")
        config_path = os.path.join(model_path, "config.json")
        if not os.path.exists(config_path):
            print(f"   错误: 配置文件不存在: {config_path}")
            return False
        
        # 手动加载tokenizer文件
        print(f"5. 尝试手动加载tokenizer...")
        tokenizer_config_path = os.path.join(model_path, "tokenizer_config.json")
        tokenizer_path = os.path.join(model_path, "tokenizer.json")
        
        if not os.path.exists(tokenizer_config_path) or not os.path.exists(tokenizer_path):
            print(f"   错误: tokenizer文件不完整")
            return False
        
        # 使用PreTrainedTokenizerFast直接加载
        try:
            tokenizer = PreTrainedTokenizerFast(
                tokenizer_file=tokenizer_path,
                eos_token="<|endoftext|>",
                pad_token="<|endoftext|>"
            )
            print(f"   tokenizer手动加载成功: {type(tokenizer).__name__}")
        except Exception as e:
            print(f"   tokenizer手动加载失败: {str(e)}")
            return False
        
        # 尝试加载模型
        print(f"6. 尝试加载模型...")
        model_file = os.path.join(model_path, "model.safetensors")
        if not os.path.exists(model_file):
            model_file = os.path.join(model_path, "pytorch_model.bin")
            if not os.path.exists(model_file):
                print(f"   错误: 找不到模型权重文件")
                return False
        
        # 使用AutoModelForCausalLM尝试加载
        try:
            config = AutoConfig.from_pretrained(model_path, local_files_only=True)
            print(f"   模型配置: {config.model_type}, 参数量: {config.vocab_size}")
            
            print(f"   尝试使用AutoModelForCausalLM加载模型...")
            model = AutoModelForCausalLM.from_config(config)
            print(f"   模型从配置加载成功: {type(model).__name__}")
            
            # 尝试加载权重
            print(f"   模型结构已创建，但权重尚未加载")
            print(f"   注意: 在旧版transformers中可能无法加载最新模型的权重")
        except Exception as e:
            print(f"   模型加载失败: {str(e)}")
            return False
        
        print("测试完成! 模型基本结构可以创建，但需要更新transformers版本才能完全加载。")
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
    
    # 测试模型加载
    success = test_model_with_fallback(model_path)
    sys.exit(0 if success else 1) 