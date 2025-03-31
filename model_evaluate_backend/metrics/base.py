"""
评估指标基类
"""
from abc import ABC, abstractmethod


class BaseMetric(ABC):
    """
    评估指标基类
    """
    def __init__(self, name):
        self.name = name
        
    @abstractmethod
    def compute(self, predictions, references, **kwargs):
        """
        计算指标
        
        Args:
            predictions: 模型预测结果列表
            references: 参考答案列表
            **kwargs: 其他参数
            
        Returns:
            dict: 包含指标结果的字典
        """
        pass
    
    def __call__(self, predictions, references, **kwargs):
        """
        调用计算函数
        """
        return self.compute(predictions, references, **kwargs)
    
    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name})" 