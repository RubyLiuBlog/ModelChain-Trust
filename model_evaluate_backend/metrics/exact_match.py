"""
精确匹配评估指标实现
"""
import re
from model_evaluate_demo.utils.registry import METRICS
from model_evaluate_demo.metrics.base import BaseMetric


@METRICS.register('exact_match')
class ExactMatchMetric(BaseMetric):
    """
    精确匹配评估指标
    
    检查预测结果是否与参考结果完全匹配。
    """
    def __init__(self):
        super().__init__('exact_match')
        
    def compute(self, predictions, references, **kwargs):
        """
        计算精确匹配分数
        
        Args:
            predictions: 模型生成的文本列表
            references: 参考答案列表
            **kwargs:
                - normalize: 是否归一化文本，默认为True
                - case_sensitive: 是否区分大小写，默认为False
                
        Returns:
            dict: 包含精确匹配分数和详细信息的字典
        """
        if len(predictions) != len(references):
            raise ValueError(f"预测数量 ({len(predictions)}) 与参考答案数量 ({len(references)}) 不匹配")
        
        normalize = kwargs.get('normalize', True)
        case_sensitive = kwargs.get('case_sensitive', False)
        
        # 预处理文本
        processed_predictions = []
        for pred in predictions:
            if normalize:
                pred = self._normalize_text(pred)
            if not case_sensitive:
                pred = pred.lower()
            processed_predictions.append(pred)
        
        processed_references = []
        for ref in references:
            if normalize:
                ref = self._normalize_text(ref)
            if not case_sensitive:
                ref = ref.lower()
            processed_references.append(ref)
        
        # 计算匹配
        correct = 0
        details = []
        
        for i, (pred, ref) in enumerate(zip(processed_predictions, processed_references)):
            is_match = pred == ref
            if is_match:
                correct += 1
                
            details.append({
                'index': i,
                'prediction': predictions[i],
                'processed_prediction': processed_predictions[i],
                'reference': references[i],
                'processed_reference': processed_references[i],
                'match': is_match
            })
        
        exact_match_score = correct / len(predictions) if predictions else 0
        
        return {
            'score': exact_match_score,
            'correct': correct,
            'total': len(predictions),
            'details': details
        }
    
    def _normalize_text(self, text):
        """
        对文本进行归一化处理
        """
        if not text:
            return ""
        
        # 替换多个空格为单个空格
        text = re.sub(r'\s+', ' ', text)
        
        # 删除前后空格
        text = text.strip()
        
        # 删除标点符号
        for char in ['.', ',', ';', ':', '?', '!']:
            text = text.replace(char, '')
            
        return text 