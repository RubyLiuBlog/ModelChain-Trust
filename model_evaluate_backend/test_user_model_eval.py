import sys
import os

# 在导入任何transformers库前设置离线环境变量
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_model_directory(model_path):
    """检查模型目录的详细信息和必要文件"""
    if not os.path.exists(model_path):
        print(f"错误: 模型路径不存在: {model_path}")
        return False

    print(f"模型路径存在: {model_path}")
    
    # 列出目录内容
    files = os.listdir(model_path)
    print(f"目录包含 {len(files)} 个文件:")
    for file in files:
        file_path = os.path.join(model_path, file)
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        print(f"  - {file} ({file_size:.2f} MB)")
    
    # 检查必要的模型文件
    required_files = ["config.json", "tokenizer_config.json"]
    model_files = ["model.safetensors", "pytorch_model.bin"]
    
    missing_files = [f for f in required_files if f not in files]
    if missing_files:
        print(f"警告: 缺少必要的配置文件: {', '.join(missing_files)}")
    
    has_model_file = any(model_file in files for model_file in model_files)
    if not has_model_file:
        print(f"警告: 未找到模型权重文件。应该包含以下文件之一: {', '.join(model_files)}")
    
    return len(missing_files) == 0 and has_model_file

# 检查模型路径
model_path = "/home/bugsmith/qwen"
model_dir_ok = check_model_directory(model_path)

if not model_dir_ok:
    print("模型目录检查未通过，可能会导致评测失败。是否继续? (y/n)")
    response = input().strip().lower()
    if response != 'y':
        print("已取消评测。")
        sys.exit(0)

# 导入模块
from model_evaluate_demo.api import evaluate_model
import torch

# 获取当前transformers版本
import importlib
transformers_version = importlib.import_module('transformers').__version__
print(f"当前使用的transformers版本: {transformers_version}")

# 评测模型
try:
    print(f"\n开始评测模型: {model_path}...")
    results = evaluate_model(
        model_path=model_path,  # 使用本地模型路径
        model_type="huggingface",
        dataset_name="math",
        metrics=["accuracy"],
        max_samples=1,  # 先测试一个样本
        offline=True,  # 确保离线模式
        trust_remote_code=True,  # Qwen模型通常需要trust_remote_code
        local_files_only=True,  # 确保只使用本地文件
        device="cuda" if torch.cuda.is_available() else "cpu",  # 自动检测设备
        debug=True  # 打开调试输出
    )
    
    # 返回结果给用户
    print("\n评测结果:")
    print(results)
    
except Exception as e:
    print(f"评测过程出错: {str(e)}")
    import traceback
    traceback.print_exc()