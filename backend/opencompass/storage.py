import os
import shutil
import uuid
import logging
from datetime import datetime
from django.conf import settings

logger = logging.getLogger(__name__)

class ModelStorage:
    def __init__(self):
        self.check_storage_dirs()

    def check_storage_dirs(self):
        """检查并创建必要的存储目录"""
        try:
            os.makedirs(settings.MODEL_ROOT_DIR, exist_ok=True)
            os.makedirs(settings.README_DIR, exist_ok=True)
        except Exception as e:
            logger.error(f"创建存储目录失败: {str(e)}")
            raise Exception(f"无法创建存储目录: {str(e)}")

    def create_model_directory(self, model_name):
        """
        为模型创建唯一的目录
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = uuid.uuid4().hex[:8]
        dir_name = f"{model_name}_{timestamp}_{unique_id}"
        model_dir = os.path.join(settings.MODEL_ROOT_DIR, dir_name)
        os.makedirs(model_dir, exist_ok=True)
        return dir_name, model_dir

    def store_model_folder(self, folder_path, model_name):
        """
        存储模型文件夹
        
        Args:
            folder_path: 源文件夹路径
            model_name: 模型名称
            
        Returns:
            str: 模型目录的相对路径
        """
        try:
            # 创建新的模型目录
            dir_name, model_dir = self.create_model_directory(model_name)
            
            # 复制文件夹内容
            for item in os.listdir(folder_path):
                source = os.path.join(folder_path, item)
                destination = os.path.join(model_dir, item)
                
                if os.path.isdir(source):
                    shutil.copytree(source, destination)
                else:
                    shutil.copy2(source, destination)
            
            logger.info(f"模型文件夹复制成功: {model_dir}")
            return os.path.join('models', dir_name)
            
        except Exception as e:
            logger.error(f"存储模型文件夹失败: {str(e)}")
            if os.path.exists(model_dir):
                shutil.rmtree(model_dir)
            raise Exception(f"存储模型文件夹失败: {str(e)}")

    def store_readme(self, readme_file, model_name):
        """
        存储README文档
        
        Args:
            readme_file: README文件对象
            model_name: 模型名称
            
        Returns:
            str: README文件的相对路径
        """
        try:
            # 检查文件扩展名
            _, ext = os.path.splitext(readme_file.name)
            if ext.lower() not in settings.ALLOWED_DOC_EXTENSIONS:
                raise Exception("不支持的文档格式")

            # 生成唯一文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_id = uuid.uuid4().hex[:8]
            filename = f"{model_name}_readme_{timestamp}_{unique_id}{ext}"
            file_path = os.path.join(settings.README_DIR, filename)
            
            # 保存文件
            with open(file_path, 'wb+') as destination:
                for chunk in readme_file.chunks():
                    destination.write(chunk)
            
            logger.info(f"README文档保存成功: {file_path}")
            return os.path.join('readmes', filename)
            
        except Exception as e:
            logger.error(f"存储README文档失败: {str(e)}")
            raise Exception(f"存储README文档失败: {str(e)}")

    def get_model_path(self, relative_path):
        """获取模型的完整路径"""
        return os.path.join(settings.MODEL_ROOT_DIR, relative_path)

    def get_readme_path(self, relative_path):
        """获取README的完整路径"""
        return os.path.join(settings.README_DIR, relative_path)

    def delete_model(self, relative_path):
        """删除模型文件夹"""
        try:
            full_path = self.get_model_path(relative_path)
            if os.path.exists(full_path):
                shutil.rmtree(full_path)
                logger.info(f"模型文件夹删除成功: {full_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"删除模型文件夹失败: {str(e)}")
            raise Exception(f"删除模型文件夹失败: {str(e)}")