"""
GSM8K数据集实现
"""
import os
import json
import requests
from model_evaluate_demo.utils.registry import DATASETS
from model_evaluate_demo.datasets.base import BaseDataset


@DATASETS.register('gsm8k')
class GSM8KDataset(BaseDataset):
    """
    GSM8K数据集
    
    GSM8K是一个由8.5K个高质量Grade School数学问题组成的数据集，这些问题需要2到8个步骤来解决。
    """
    def __init__(self, **kwargs):
        super().__init__('gsm8k', **kwargs)
        self.subset = kwargs.get('subset', 'main')
        self.max_samples = kwargs.get('max_samples', None)
        
        # 定义默认提示模板，使用双花括号格式
        self.default_template = kwargs.get('template', 
            "问题: {{question}}\n\n请一步步思考，最后给出答案。"
        )
        
        # 定义URLs
        self.urls = {
            'train': 'https://raw.githubusercontent.com/openai/grade-school-math/master/grade_school_math/data/train.jsonl',
            'test': 'https://raw.githubusercontent.com/openai/grade-school-math/master/grade_school_math/data/test.jsonl'
        }
        
        # 检查是否提供了数据路径，如果没有则设置默认值
        if not self.data_path:
            # 尝试多个可能的本地数据路径
            possible_paths = [
                # 相对于当前工作目录
                os.path.join("data", "gsm8k"),
                # 相对于项目根目录
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "gsm8k"),
                # 相对于用户home目录
                os.path.join(os.path.expanduser("~"), "model_evaluate_demo", "data", "gsm8k"),
                # 相对于用户home目录
                os.path.join(os.path.expanduser("~"), "data", "gsm8k")
            ]
            
            # 选择第一个存在的路径
            for path in possible_paths:
                if os.path.exists(path):
                    self.data_path = path
                    break
                    
        print(f"GSM8K数据集路径: {self.data_path if self.data_path else '未设置'}")
        
    def load(self):
        """加载GSM8K数据集"""
        cache_key = f"gsm8k_{self.subset}_{self.split}"
        
        # 尝试从缓存加载
        cached_data = self.load_from_cache(cache_key)
        if cached_data is not None:
            self.data = cached_data
            return self
        
        # 如果指定了本地数据路径
        if self.data_path and os.path.exists(self.data_path):
            # 首先检查是否有test.jsonl文件
            test_file = os.path.join(self.data_path, "test.jsonl")
            if os.path.exists(test_file):
                print(f"从本地文件加载GSM8K测试数据: {test_file}")
                return self._load_local_jsonl(test_file)
                
            # 检查标准的split文件
            split_file = os.path.join(self.data_path, f"{self.split}.jsonl")
            if os.path.exists(split_file):
                print(f"从本地文件加载GSM8K {self.split}数据: {split_file}")
                return self._load_local_jsonl(split_file)
                
            return self._load_from_local()
        
        # 否则从URL下载
        return self._load_from_url()
    
    def _load_local_jsonl(self, file_path):
        """从本地JSONL文件加载数据"""
        try:
            data = []
            line_count = 0
            
            # 首先计算总行数
            with open(file_path, 'r', encoding='utf-8') as f:
                for _ in f:
                    line_count += 1
            
            # 如果max_samples已设置且小于总行数，只处理max_samples的数据
            process_count = min(line_count, self.max_samples) if self.max_samples else line_count
            print(f"JSONL文件共有{line_count}行，将处理前{process_count}行")
            
            # 加载数据
            with open(file_path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    if self.max_samples and i >= self.max_samples:
                        break
                        
                    if line.strip():
                        try:
                            item = json.loads(line.strip())
                            processed_item = self._process_item(item)
                            data.append(processed_item)
                        except json.JSONDecodeError:
                            print(f"跳过无效的JSON行: {line[:50]}...")
                    
            self.data = data
            
            # 保存到缓存
            cache_key = f"gsm8k_{self.subset}_{self.split}"
            self.save_to_cache(cache_key, data)
            
            print(f"从本地加载了 {len(data)} 个GSM8K样本")
            return self
            
        except Exception as e:
            print(f"从本地加载GSM8K数据集失败: {str(e)}")
            # 回退到创建测试数据
            self.data = self._create_test_data()
            return self
    
    def _load_from_local(self):
        """从本地加载数据"""
        try:
            file_path = os.path.join(self.data_path, f"{self.split}.jsonl")
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"找不到文件: {file_path}")
                
            data = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    item = json.loads(line.strip())
                    processed_item = self._process_item(item)
                    data.append(processed_item)
                    
            if self.max_samples and len(data) > self.max_samples:
                data = data[:self.max_samples]
                
            self.data = data
            
            # 保存到缓存
            cache_key = f"gsm8k_{self.subset}_{self.split}"
            self.save_to_cache(cache_key, data)
            
            print(f"从本地加载了 {len(data)} 个GSM8K样本")
            return self
            
        except Exception as e:
            print(f"从本地加载GSM8K数据集失败: {str(e)}")
            raise
    
    def _load_from_url(self):
        """从URL下载数据"""
        try:
            if self.split not in self.urls:
                raise ValueError(f"分割'{self.split}'不可用。可用的分割: {list(self.urls.keys())}")
                
            url = self.urls[self.split]
            print(f"从URL下载GSM8K数据: {url}")
            
            # 设置超时参数，避免长时间等待
            response = requests.get(url, timeout=10)  # 10秒超时
            response.raise_for_status()
            
            data = []
            for line in response.text.splitlines():
                if line.strip():
                    item = json.loads(line.strip())
                    processed_item = self._process_item(item)
                    data.append(processed_item)
            
            if self.max_samples and len(data) > self.max_samples:
                data = data[:self.max_samples]
                
            self.data = data
            
            # 保存到缓存
            cache_key = f"gsm8k_{self.subset}_{self.split}"
            self.save_to_cache(cache_key, data)
            
            print(f"从URL加载了 {len(data)} 个GSM8K样本")
            return self
            
        except Exception as e:
            print(f"从URL加载GSM8K数据集失败: {str(e)}")
            print("创建本地示例数据作为备用...")
            self.data = self._create_test_data()
            return self
            
    def _create_test_data(self):
        """创建测试数据，当无法从URL或本地加载时使用"""
        test_data = [
            {
                'question': '小明有5个苹果，小红给了他3个苹果。小明现在有多少个苹果？',
                'full_answer': '小明开始有5个苹果。\n小红给了他3个苹果。\n所以小明现在有 5 + 3 = 8 个苹果。\n答案是 8。',
                'answer': '8'
            },
            {
                'question': '一家商店有24个鸡蛋。如果他们卖出了一半的鸡蛋，然后又卖出了4个，他们还剩下多少个鸡蛋？',
                'full_answer': '商店开始有24个鸡蛋。\n他们卖出了一半，也就是 24 ÷ 2 = 12 个鸡蛋。\n然后又卖出了4个，所以总共卖出了 12 + 4 = 16 个鸡蛋。\n剩下的鸡蛋数量是 24 - 16 = 8 个。\n答案是 8。',
                'answer': '8'
            },
            {
                'question': '一辆车以每小时60公里的速度行驶，2.5小时后行驶了多少公里？',
                'full_answer': '车速是每小时60公里。\n行驶时间是2.5小时。\n行驶距离 = 速度 × 时间 = 60 × 2.5 = 150公里。\n答案是 150。',
                'answer': '150'
            }
        ]
        
        # 保存到缓存以避免下次再次创建
        cache_key = f"gsm8k_sample_{self.split}"
        self.save_to_cache(cache_key, test_data)
        
        print(f"创建了 {len(test_data)} 个GSM8K示例")
        return test_data
    
    def _process_item(self, item):
        """处理原始数据项"""
        # 提取问题和答案
        question = item.get('question', '')
        answer = item.get('answer', '')
        
        # 提取最终的数值答案
        final_answer = self._extract_final_answer(answer)
        
        return {
            'question': question,
            'full_answer': answer,
            'answer': final_answer
        }
    
    def _extract_final_answer(self, answer_text):
        """从答案文本中提取最终的数值答案"""
        try:
            # GSM8K通常在答案的最后一行包含"The answer is X"
            lines = answer_text.strip().split('\n')
            last_line = lines[-1].strip()
            
            # 尝试提取"The answer is X"模式
            if "answer is" in last_line.lower():
                parts = last_line.lower().split("answer is")
                if len(parts) > 1:
                    # 提取数字部分
                    number_part = parts[1].strip()
                    # 移除美元符号等
                    for char in ['$', ',', '\\$']:
                        number_part = number_part.replace(char, '')
                    # 移除后面的句号或其他非数字字符
                    import re
                    matches = re.findall(r'-?\d+\.?\d*', number_part)
                    if matches:
                        return matches[0]
            
            # 如果上面的方法不成功，尝试查找最后出现的数字
            import re
            all_numbers = re.findall(r'-?\d+\.?\d*', answer_text)
            if all_numbers:
                return all_numbers[-1]
                
            return answer_text  # 如果无法提取，返回原始答案
            
        except Exception:
            return answer_text 