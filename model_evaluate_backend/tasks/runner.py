"""
任务运行器实现
"""
import os
import json
import yaml
import time
import datetime
from concurrent.futures import ThreadPoolExecutor
from model_evaluate_demo.tasks.evaluator import Evaluator
from model_evaluate_demo.utils.registry import MODELS, DATASETS, METRICS


class TaskRunner:
    """
    任务运行器类
    
    负责从配置文件加载评测任务并管理评测任务的执行。
    """
    def __init__(self, **kwargs):
        self.config_path = kwargs.get('config_path')
        self.output_dir = kwargs.get('output_dir', 'outputs')
        self.max_workers = kwargs.get('max_workers', 1)
        self.debug = kwargs.get('debug', False)
        self.evaluator = Evaluator(output_dir=self.output_dir, debug=self.debug)
        
    def run_from_config(self, config_path=None):
        """
        从配置文件运行评测任务
        
        Args:
            config_path: 配置文件路径，如果为None则使用初始化时提供的路径
            
        Returns:
            dict: 所有任务的结果
        """
        if config_path is not None:
            self.config_path = config_path
            
        if not self.config_path:
            raise ValueError("未提供配置文件路径")
            
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        
        # 加载配置
        config = self._load_config(self.config_path)
        
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 执行任务
        return self.run_from_dict(config)
    
    def run_from_dict(self, config):
        """
        从配置字典运行评测任务
        
        Args:
            config: 配置字典
            
        Returns:
            dict: 所有任务的结果
        """
        # 检查配置必要字段
        if 'tasks' not in config:
            raise ValueError("配置中缺少'tasks'字段")
            
        tasks = config['tasks']
        if not tasks:
            print("警告: 未找到任务配置")
            return {}
            
        # 记录任务开始时间
        start_time = time.time()
        
        # 准备结果记录
        all_results = {
            'timestamp': datetime.datetime.now().isoformat(),
            'task_count': len(tasks),
            'tasks': []
        }
        
        # 单个任务执行函数
        def execute_task(task_config):
            try:
                # 提取任务参数
                task_name = task_config.get('name', f"task_{int(time.time())}")
                model_config = task_config.get('model')
                dataset_config = task_config.get('dataset')
                metrics_config = task_config.get('metrics', ['accuracy'])
                eval_config = task_config.get('eval_config', {})
                
                if not model_config:
                    raise ValueError(f"任务 '{task_name}' 缺少模型配置")
                if not dataset_config:
                    raise ValueError(f"任务 '{task_name}' 缺少数据集配置")
                
                # 准备模型参数
                if isinstance(model_config, str):
                    model_name = model_config
                    model_kwargs = {}
                    model_name_or_path = model_name
                else:
                    model_name = model_config.get('name')
                    model_kwargs = {k: v for k, v in model_config.items() if k != 'name'}
                    
                    # 修复model_name_or_path参数，确保正确传递给模型
                    if 'model_name' in model_kwargs:
                        model_name_or_path = model_kwargs.pop('model_name')
                    else:
                        model_name_or_path = model_name
                
                # 准备数据集参数
                if isinstance(dataset_config, str):
                    dataset_name = dataset_config
                    dataset_kwargs = {}
                else:
                    dataset_name = dataset_config.get('name')
                    dataset_kwargs = {k: v for k, v in dataset_config.items() if k != 'name'}
                
                # 初始化模型
                try:
                    model_cls = MODELS.get(model_name)
                    if model_name == 'openai':
                        model = model_cls(model_name_or_path, **model_kwargs)
                    else:
                        model = model_cls(model_name_or_path, **model_kwargs)
                except KeyError:
                    raise ValueError(f"未知模型: {model_name}。请确保已注册该模型。")
                
                # 初始化数据集
                try:
                    dataset_cls = DATASETS.get(dataset_name)
                    dataset = dataset_cls(**dataset_kwargs)
                except KeyError:
                    raise ValueError(f"未知数据集: {dataset_name}。请确保已注册该数据集。")
                
                # 初始化评估指标
                metric_instances = []
                for metric_config in metrics_config:
                    if isinstance(metric_config, str):
                        metric_name = metric_config
                        metric_kwargs = {}
                    else:
                        metric_name = metric_config.get('name')
                        metric_kwargs = {k: v for k, v in metric_config.items() if k != 'name'}
                        
                    try:
                        metric_cls = METRICS.get(metric_name)
                        metric_instances.append(metric_cls(**metric_kwargs))
                    except KeyError:
                        raise ValueError(f"未知评估指标: {metric_name}。请确保已注册该指标。")
                
                # 运行评测
                print(f"\n执行任务: {task_name}")
                print(f"模型: {model_name}, 数据集: {dataset_name}, 指标: {', '.join([m.name for m in metric_instances])}")
                
                result = self.evaluator.evaluate(model, dataset, metric_instances, **eval_config)
                result['task_name'] = task_name
                
                return result
                
            except Exception as e:
                print(f"任务执行失败: {str(e)}")
                return {
                    'task_name': task_config.get('name', 'unknown'),
                    'error': str(e),
                    'timestamp': datetime.datetime.now().isoformat()
                }
        
        # 执行所有任务
        if self.max_workers > 1 and len(tasks) > 1:
            # 并行执行
            print(f"使用 {self.max_workers} 个工作线程并行执行 {len(tasks)} 个任务")
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                task_results = list(executor.map(execute_task, tasks))
        else:
            # 串行执行
            print(f"串行执行 {len(tasks)} 个任务")
            task_results = [execute_task(task) for task in tasks]
            
        # 记录任务结果
        all_results['tasks'] = task_results
        
        # 计算总耗时
        elapsed_time = time.time() - start_time
        all_results['elapsed_time'] = elapsed_time
        print(f"\n所有任务完成，总耗时: {elapsed_time:.2f}秒")
        
        # 保存总结果
        self._save_summary(all_results)
        
        return all_results
    
    def _load_config(self, config_path):
        """
        加载配置文件
        """
        file_ext = os.path.splitext(config_path)[1].lower()
        
        try:
            if file_ext in ['.yml', '.yaml']:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            elif file_ext == '.json':
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                raise ValueError(f"不支持的配置文件类型: {file_ext}")
        except Exception as e:
            raise ValueError(f"加载配置文件失败: {str(e)}")
    
    def _save_summary(self, results):
        """
        保存评测结果摘要
        """
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_summary.json"
        filepath = os.path.join(self.output_dir, filename)
        
        # 简化结果以避免文件过大
        summary = {
            'timestamp': results['timestamp'],
            'task_count': results['task_count'],
            'elapsed_time': results['elapsed_time'],
            'tasks': []
        }
        
        for task in results['tasks']:
            task_summary = {
                'task_name': task.get('task_name', 'unknown'),
                'model_name': task.get('model_name', 'unknown'),
                'dataset_name': task.get('dataset_name', 'unknown'),
                'samples_count': task.get('samples_count', 0),
                'elapsed_time': task.get('elapsed_time', 0),
                'metrics': {}
            }
            
            # 只保留评估指标的分数
            for metric_name, metric_result in task.get('metrics', {}).items():
                if isinstance(metric_result, dict) and 'score' in metric_result:
                    task_summary['metrics'][metric_name] = metric_result['score']
                else:
                    task_summary['metrics'][metric_name] = metric_result
                    
            summary['tasks'].append(task_summary)
        
        # 保存为JSON文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
            
        print(f"结果摘要已保存到: {filepath}") 