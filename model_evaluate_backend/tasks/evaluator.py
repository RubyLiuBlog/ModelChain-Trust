"""
评测器实现
"""
import os
import json
import time
import datetime
from tqdm import tqdm
from model_evaluate_demo.utils.registry import MODELS, DATASETS, METRICS


class Evaluator:
    """
    评测器类
    
    负责协调模型、数据集和评估指标，执行评测流程。
    """
    def __init__(self, **kwargs):
        self.output_dir = kwargs.get('output_dir', 'outputs')
        self.debug = kwargs.get('debug', False)
        
    def evaluate(self, model, dataset, metrics, **kwargs):
        """
        执行评测
        
        Args:
            model: 模型实例或模型名称
            dataset: 数据集实例或数据集名称
            metrics: 评估指标列表或指标名称列表
            **kwargs:
                - prompt_template: 提示模板
                - batch_size: 推理批次大小
                - max_samples: 最大样本数
                - generation_kwargs: 生成参数
                
        Returns:
            dict: 评测结果
        """
        # 准备模型
        if isinstance(model, str):
            try:
                model_cls = MODELS.get(model)
                model = model_cls(model)
            except KeyError:
                raise ValueError(f"未知模型: {model}。请确保已注册该模型。")
        
        # 准备数据集
        if isinstance(dataset, str):
            try:
                dataset_cls = DATASETS.get(dataset)
                dataset = dataset_cls()
            except KeyError:
                raise ValueError(f"未知数据集: {dataset}。请确保已注册该数据集。")
        
        # 加载模型和数据集
        if not hasattr(model, '_model') or model._model is None:
            model.load()
        
        if dataset.data is None:
            dataset.load()
        
        # 准备评估指标
        metric_instances = []
        for metric in metrics:
            if isinstance(metric, str):
                try:
                    metric_cls = METRICS.get(metric)
                    metric_instances.append(metric_cls())
                except KeyError:
                    raise ValueError(f"未知评估指标: {metric}。请确保已注册该指标。")
            else:
                metric_instances.append(metric)
        
        # 准备参数
        prompt_template = kwargs.get('prompt_template', dataset.default_template if hasattr(dataset, 'default_template') else None)
        batch_size = kwargs.get('batch_size', 16)
        max_samples = kwargs.get('max_samples', None)
        generation_kwargs = kwargs.get('generation_kwargs', {})
        
        # 限制样本数
        if max_samples and max_samples < len(dataset):
            indices = list(range(max_samples))
        else:
            indices = list(range(len(dataset)))
        
        # 记录开始时间
        start_time = time.time()
        
        # 准备结果记录
        results = {
            'model_name': model.model_name,
            'dataset_name': dataset.name,
            'samples_count': len(indices),
            'prompt_template': prompt_template,
            'generation_kwargs': generation_kwargs,
            'timestamp': datetime.datetime.now().isoformat(),
            'metrics': {},
            'samples': []
        }
        
        # 准备提示和参考答案
        prompts = []
        references = []
        
        for idx in indices:
            prompt = dataset.get_prompt(idx, template=prompt_template)
            prompts.append(prompt)
            
            item = dataset[idx]
            reference = item.get('answer', '')
            references.append(reference)
            
        # 分批处理
        predictions = []
        
        print(f"生成回复中...")
        for i in tqdm(range(0, len(prompts), batch_size)):
            batch_prompts = prompts[i:i+batch_size]
            
            try:
                batch_predictions = model.generate(batch_prompts, **generation_kwargs)
                predictions.extend(batch_predictions)
                
                if self.debug:
                    print(f"\n样本 {i}:")
                    print(f"提示: {batch_prompts[0][:100]}...")
                    print(f"生成: {batch_predictions[0][:100]}...")
                    
            except Exception as e:
                print(f"批次 {i}-{i+batch_size-1} 生成失败: {str(e)}")
                # 对失败的批次填充空字符串
                predictions.extend([""] * len(batch_prompts))
        
        # 记录样本详情
        for i, (prompt, prediction, reference) in enumerate(zip(prompts, predictions, references)):
            sample_info = {
                'idx': indices[i],
                'prompt': prompt,
                'prediction': prediction,
                'reference': reference
            }
            results['samples'].append(sample_info)
        
        # 计算评估指标
        for metric in metric_instances:
            try:
                metric_result = metric.compute(predictions, references)
                results['metrics'][metric.name] = metric_result
                print(f"指标 {metric.name}: {metric_result['score']:.4f}")
            except Exception as e:
                print(f"计算指标 {metric.name} 失败: {str(e)}")
                results['metrics'][metric.name] = {'error': str(e)}
        
        # 记录总耗时
        elapsed_time = time.time() - start_time
        results['elapsed_time'] = elapsed_time
        print(f"评测完成，耗时: {elapsed_time:.2f}秒")
        
        # 保存结果
        self._save_results(results)
        
        return results
    
    def _save_results(self, results):
        """
        保存评测结果
        """
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        model_name = results['model_name'].split('/')[-1]
        dataset_name = results['dataset_name']
        
        filename = f"{timestamp}_{model_name}_{dataset_name}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        # 保存为JSON文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        print(f"结果已保存到: {filepath}") 