from .celery import app
from celery_progress.backend import ProgressRecorder
import os
import shutil
import zipfile
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@app.task(bind=True)
def process_model_files(self, model_path, readme_path, address, model_id):
    """处理模型文件的异步任务"""
    try:
        # 创建进度记录器
        progress_recorder = ProgressRecorder(self)
        total_steps = 6  # 增加了解压步骤
        current_step = 0

        # 步骤1: 验证文件
        progress_recorder.set_progress(current_step, total_steps, f'验证文件 {model_id}')
        if not (os.path.exists(model_path) and os.path.exists(readme_path)):
            raise FileNotFoundError("模型文件或README文件不存在")
        current_step += 1

        # 步骤2: 创建目标目录
        progress_recorder.set_progress(current_step, total_steps, '创建目标目录')
        model_dir = os.path.join(settings.MODEL_ROOT_DIR, model_id)
        readme_dir = os.path.join(settings.README_DIR, model_id)
        os.makedirs(model_dir, exist_ok=True)
        os.makedirs(readme_dir, exist_ok=True)
        current_step += 1

        # 步骤3: 处理模型文件
        progress_recorder.set_progress(current_step, total_steps, '处理模型文件')
        final_model_path = os.path.join(model_dir, os.path.basename(model_path))
        shutil.move(model_path, final_model_path)
        current_step += 1

        # 步骤4: 解压模型文件（如果是压缩文件）
        progress_recorder.set_progress(current_step, total_steps, '解压模型文件')
        if zipfile.is_zipfile(final_model_path):
            with zipfile.ZipFile(final_model_path, 'r') as zip_ref:
                # 创建临时解压目录
                extract_dir = os.path.join(model_dir, 'extracted')
                os.makedirs(extract_dir, exist_ok=True)
                # 解压文件
                zip_ref.extractall(extract_dir)
                # 删除原始zip文件
                os.remove(final_model_path)
                # 将解压后的文件移动到模型目录
                for item in os.listdir(extract_dir):
                    shutil.move(
                        os.path.join(extract_dir, item),
                        os.path.join(model_dir, item)
                    )
                # 删除临时解压目录
                shutil.rmtree(extract_dir)
        current_step += 1

        # 步骤5: 处理README文件
        progress_recorder.set_progress(current_step, total_steps, '处理README文件')
        final_readme_path = os.path.join(readme_dir, os.path.basename(readme_path))
        shutil.move(readme_path, final_readme_path)
        current_step += 1

        # 步骤6: 清理临时文件
        progress_recorder.set_progress(current_step, total_steps, '清理临时文件')
        temp_dir = os.path.dirname(model_path)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

        return {
            'status': 'success',
            'model_id': model_id,
            'model_path': model_dir,  # 返回模型目录而不是具体文件路径
            'readme_path': final_readme_path,
            'message': '文件处理完成'
        }

    except Exception as e:
        logger.error(f"处理模型文件失败 (model_id: {model_id}): {str(e)}")
        # 清理失败时的文件
        try:
            if os.path.exists(model_dir):
                shutil.rmtree(model_dir)
            if os.path.exists(readme_dir):
                shutil.rmtree(readme_dir)
        except Exception as cleanup_error:
            logger.error(f"清理失败文件时出错: {str(cleanup_error)}")
            
        return {
            'status': 'error',
            'model_id': model_id,
            'message': str(e)
        }


