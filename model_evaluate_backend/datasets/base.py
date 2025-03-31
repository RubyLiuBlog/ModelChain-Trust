"""
数据集基类，定义统一接口
"""
from abc import ABC, abstractmethod
import os
import json
import re


class BaseDataset(ABC):
    """
    数据集基类
    """
    def __init__(self, name, **kwargs):
        self.name = name
        self.data_path = kwargs.get('data_path', None)
        self.cache_path = kwargs.get('cache_path', '.cache')
        self.split = kwargs.get('split', 'test')
        self.data = None
        
    @abstractmethod
    def load(self):
        """加载数据集"""
        pass
    
    def get_item(self, idx):
        """获取样本"""
        if self.data is None:
            raise RuntimeError("数据集尚未加载，请先调用load()")
        
        if idx < 0 or idx >= len(self.data):
            raise IndexError(f"索引{idx}超出数据集范围(0~{len(self.data)-1})")
            
        return self.data[idx]
    
    def get_prompt(self, idx, template=None):
        """根据模板获取提示"""
        item = self.get_item(idx)
        
        if template is None:
            # 默认使用直接返回问题
            return item.get('question', '')
        
        # 首先检查是否使用了双花括号格式 {{variable}}
        double_brace_matches = re.findall(r"\{\{(\w+)\}\}", template)
        
        if double_brace_matches:
            # 使用双花括号格式的情况
            prompt = template
            for key in double_brace_matches:
                if key in item:
                    # 替换 {{key}} 为实际值
                    prompt = prompt.replace(f"{{{{{key}}}}}", str(item[key]))
                else:
                    raise KeyError(f"模板中包含数据集中不存在的键: {key}")
            return prompt
        else:
            # 使用传统的format格式化方法
            try:
                return template.format(**item)
            except KeyError as e:
                raise KeyError(f"模板中包含数据集中不存在的键: {e}")
            
    def __len__(self):
        return len(self.data) if self.data is not None else 0
    
    def __getitem__(self, idx):
        return self.get_item(idx)
    
    def save_to_cache(self, filename, data):
        """保存数据到缓存"""
        os.makedirs(self.cache_path, exist_ok=True)
        cache_file = os.path.join(self.cache_path, f"{filename}.json")
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"数据已缓存到 {cache_file}")
        
    def load_from_cache(self, filename):
        """从缓存加载数据"""
        cache_file = os.path.join(self.cache_path, f"{filename}.json")
        
        if not os.path.exists(cache_file):
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"从缓存 {cache_file} 加载数据")
            return data
        except Exception as e:
            print(f"加载缓存失败: {str(e)}")
            return None 