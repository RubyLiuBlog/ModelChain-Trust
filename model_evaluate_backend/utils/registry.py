"""
组件注册表 - 用于管理所有模型、数据集和评测指标
"""

class Registry:
    """组件注册表类"""
    
    def __init__(self, name):
        self._name = name
        self._registry = {}
    
    def register(self, name=None):
        """注册装饰器"""
        def _register(cls):
            key = name or cls.__name__
            if key in self._registry:
                raise KeyError(f"{key} 已经在 {self._name} 注册表中存在")
            self._registry[key] = cls
            return cls
        return _register
    
    def register_module(self, name=None):
        """兼容OpenCompass的注册装饰器"""
        return self.register(name)
    
    def get(self, name):
        """获取已注册的组件"""
        if name not in self._registry:
            raise KeyError(f"{name} 未在 {self._name} 注册表中找到")
        return self._registry[name]
    
    def list(self):
        """列出所有已注册的组件"""
        return list(self._registry.keys())
    
    def __contains__(self, name):
        return name in self._registry


# 创建全局注册表
MODELS = Registry('models')
DATASETS = Registry('datasets')
METRICS = Registry('metrics')
TASKS = Registry('tasks') 