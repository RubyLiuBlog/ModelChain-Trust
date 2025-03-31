#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
升级transformers库以支持最新的Qwen1.5模型
"""

import sys
import subprocess
import importlib

def upgrade_transformers():
    """升级transformers库到最新版本"""
    try:
        # 检查当前版本
        try:
            import transformers
            current_version = transformers.__version__
            print(f"当前transformers版本: {current_version}")
        except ImportError:
            current_version = "未安装"
            print("transformers库未安装")

        # 安装/升级transformers
        print("开始升级transformers库...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "transformers>=4.38.0"])

        # 重新导入检查版本
        importlib.invalidate_caches()
        import transformers
        new_version = transformers.__version__
        print(f"升级后transformers版本: {new_version}")

        # 安装依赖库
        print("安装其他必要依赖...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "torch", "accelerate"])

        print("升级完成!")
        return True
    except Exception as e:
        print(f"升级过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = upgrade_transformers()
    sys.exit(0 if success else 1) 