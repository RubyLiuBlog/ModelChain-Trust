#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
模型评测Web前端
提供Web界面调用comprehensive_evaluation.py进行模型评测
"""

import os
import sys
import json
import time
import uuid
import threading
import subprocess
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)

# 主题配置
app.config['THEME'] = {
    'name': 'dark-purple',
    'title': 'ModelChain',
    'version': '1.0'
}

# 向所有模板注入主题信息
@app.context_processor
def inject_theme():
    return {'theme': app.config['THEME']}

# 存储评测任务
evaluation_tasks = {}

# 定义模型目录，可以通过环境变量配置
MODELS_DIR = os.environ.get('MODELS_DIR', '/home/bugsmith/model_evaluate_demo/models')

# 获取可用模型列表
def get_available_models():
    """获取可用的模型列表"""
    models = []
    for item in os.listdir(MODELS_DIR):
        item_path = os.path.join(MODELS_DIR, item)
        if os.path.isdir(item_path):
            # 简单判断是否可能是模型目录：是否包含config.json等文件
            if any(os.path.exists(os.path.join(item_path, f)) for f in ['config.json', 'pytorch_model.bin', 'model.safetensors']):
                models.append(item)
    return models

# 获取可用数据集
def get_available_datasets():
    try:
        # 尝试导入model_evaluate_demo中的函数
        from model_evaluate_demo.api import list_datasets
        return list_datasets()
    except (ImportError, AttributeError):
        # 如果导入失败，返回默认值
        return ['math', 'gsm8k']

# 更新任务状态
def update_task_status(task_id, status, result=None):
    if task_id in evaluation_tasks:
        evaluation_tasks[task_id]['status'] = status
        if result:
            evaluation_tasks[task_id]['result'] = result
        evaluation_tasks[task_id]['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 运行评测任务
def run_evaluation_task(task_id, model_path, datasets, max_samples, device=None, debug=False):
    try:
        # 检查模型路径是否存在
        if not os.path.exists(model_path):
            update_task_status(task_id, 'failed', {
                'error': f'模型路径不存在: {model_path}'
            })
            return
            
        # 检查model_evaluate_demo目录是否存在
        script_path = '/home/bugsmith/model_evaluate_demo/comprehensive_evaluation.py'
        if not os.path.exists(script_path):
            update_task_status(task_id, 'failed', {
                'error': f'评测脚本不存在: {script_path}'
            })
            return
        
        # 构建命令
        cmd = [
            'python',
            script_path,
            f'--model-path={model_path}',
            f'--datasets', *datasets,
            f'--max-samples={max_samples}',
            f'--output-dir=./outputs'
        ]
        
        if device:
            cmd.append(f'--device={device}')
        
        if debug:
            cmd.append('--debug')
        
        # 更新任务状态为运行中
        update_task_status(task_id, 'running')
        
        # 运行命令
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        stdout, stderr = process.communicate()
        
        # 检查命令是否成功
        if process.returncode == 0:
            # 获取输出目录中的结果文件
            result_files = []
            timestamp = datetime.now().strftime("%Y%m%d")
            model_name = os.path.basename(model_path)
            
            # 检查输出目录是否存在
            outputs_dir = './outputs'
            if not os.path.exists(outputs_dir):
                os.makedirs(outputs_dir, exist_ok=True)
                
            # 查找对应的结果文件
            for filename in os.listdir(outputs_dir):
                if filename.startswith(timestamp) and model_name in filename:
                    result_files.append(filename)
            
            if not result_files:
                # 如果没有找到结果文件
                update_task_status(task_id, 'failed', {
                    'stdout': stdout,
                    'stderr': stderr,
                    'error': '评测完成，但未找到结果文件'
                })
            else:
                # 更新任务状态为完成
                update_task_status(task_id, 'completed', {
                    'stdout': stdout,
                    'stderr': stderr,
                    'result_files': result_files
                })
        else:
            # 更新任务状态为失败
            error_message = stderr.strip() if stderr.strip() else f'命令返回错误代码: {process.returncode}'
            update_task_status(task_id, 'failed', {
                'stdout': stdout,
                'stderr': stderr,
                'error': error_message
            })
    
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        # 更新任务状态为失败
        update_task_status(task_id, 'failed', {
            'error': str(e),
            'traceback': error_traceback
        })

@app.route('/')
def index():
    """首页"""
    # 获取可用模型和数据集
    models = get_available_models()
    datasets = get_available_datasets()
    
    return render_template(
        'index.html',
        models=models,
        datasets=datasets,
        evaluation_tasks=evaluation_tasks
    )

@app.route('/evaluate', methods=['POST'])
def evaluate():
    """提交评测任务"""
    # 获取表单参数
    model_path = request.form.get('model_path')
    datasets = request.form.getlist('datasets')
    max_samples = int(request.form.get('max_samples', 5))
    device = request.form.get('device')
    debug = 'debug' in request.form
    
    # 处理设备参数
    if device == 'auto':
        device = None  # 自动选择设备
    
    # 验证参数
    if not model_path:
        return render_template('error.html', message='请选择模型路径')
    
    if not datasets:
        return render_template('error.html', message='请选择至少一个数据集')
    
    # 创建任务ID
    task_id = str(uuid.uuid4())
    
    # 完整模型路径
    full_model_path = os.path.join(MODELS_DIR, model_path)
    
    # 添加任务
    evaluation_tasks[task_id] = {
        'id': task_id,
        'model_path': full_model_path,
        'datasets': datasets,
        'max_samples': max_samples,
        'device': device if device else '自动选择',
        'debug': debug,
        'status': 'pending',
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # 在后台线程中运行任务
    thread = threading.Thread(
        target=run_evaluation_task,
        args=(task_id, full_model_path, datasets, max_samples, device, debug)
    )
    thread.daemon = True
    thread.start()
    
    # 重定向到任务状态页面
    return redirect(url_for('task_status', task_id=task_id))

@app.route('/tasks/<task_id>')
def task_status(task_id):
    """任务状态页面"""
    task = evaluation_tasks.get(task_id)
    
    if not task:
        return render_template('error.html', message='找不到指定的任务')
    
    return render_template('task.html', task=task)

@app.route('/api/tasks/<task_id>')
def api_task_status(task_id):
    """获取任务状态的API"""
    task = evaluation_tasks.get(task_id)
    
    if not task:
        return jsonify({'error': '找不到指定的任务'}), 404
    
    return jsonify(task)

@app.route('/api/tasks')
def api_tasks_list():
    """获取任务列表的API"""
    return jsonify({
        'tasks': list(evaluation_tasks.values())
    })

@app.route('/results/<filename>')
def view_result(filename):
    """查看结果文件"""
    try:
        result_path = os.path.join('./outputs', filename)
        
        if not os.path.exists(result_path):
            return render_template('error.html', message=f'找不到结果文件: {filename}')
        
        with open(result_path, 'r', encoding='utf-8') as f:
            result_data = json.load(f)
        
        return render_template('results.html', filename=filename, result=result_data)
    
    except Exception as e:
        return render_template('error.html', message=f'读取结果文件时出错: {str(e)}')

if __name__ == '__main__':
    os.makedirs('./outputs', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000) 