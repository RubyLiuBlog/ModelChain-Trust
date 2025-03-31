#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
下载HuggingFace模型用于离线评测
"""

import os
import sys
import argparse
import shutil

def download_model(model_id, output_dir, use_mirror=True):
    """下载指定的HuggingFace模型到本地目录"""
    try:
        # 设置镜像站点(如果需要)
        if use_mirror:
            os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
            print(f"已设置HuggingFace镜像站点: {os.environ.get('HF_ENDPOINT')}")
        
        print(f"开始下载模型: {model_id}")
        print(f"输出目录: {output_dir}")
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 导入必要的库
        print("导入transformers库...")
        from transformers import AutoTokenizer, AutoModelForCausalLM
        import torch
        
        # 下载tokenizer
        print(f"下载tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        
        # 下载模型
        print(f"下载模型...")
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float16
        )
        
        # 保存模型和tokenizer到指定目录
        print(f"保存模型和tokenizer到: {output_dir}")
        tokenizer.save_pretrained(output_dir)
        model.save_pretrained(output_dir)
        
        print("模型下载完成!")
        print(f"包含文件:")
        for file in os.listdir(output_dir):
            file_path = os.path.join(output_dir, file)
            file_size = os.path.getsize(file_path) / (1024 * 1024) # MB
            print(f"  - {file} ({file_size:.2f} MB)")
            
        return True
        
    except Exception as e:
        print(f"下载模型出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="下载HuggingFace模型用于离线评测")
    parser.add_argument("--model", type=str, default="gpt2", 
                        help="模型ID (如'gpt2', 'microsoft/phi-2'等)")
    parser.add_argument("--output", type=str, default="./downloaded_model",
                        help="模型保存目录")
    parser.add_argument("--no-mirror", action="store_true",
                        help="不使用镜像站点")
    
    args = parser.parse_args()
    
    # 下载模型
    success = download_model(
        model_id=args.model,
        output_dir=args.output,
        use_mirror=not args.no_mirror
    )
    
    return 0 if success else 1
    
if __name__ == "__main__":
    sys.exit(main()) 