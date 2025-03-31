"""
Math数据集实现
"""
import os
import json
import requests
from model_evaluate_demo.utils.registry import DATASETS
from model_evaluate_demo.datasets.base import BaseDataset


@DATASETS.register('math')
class MathDataset(BaseDataset):
    """
    Math数据集
    
    MATH数据集包含数学竞赛级别的问题，涵盖代数、几何、微积分、统计等多个领域。
    """
    def __init__(self, **kwargs):
        super().__init__('math', **kwargs)
        self.subject = kwargs.get('subject', None)  # 可以是 'algebra', 'geometry' 等
        self.difficulty = kwargs.get('difficulty', None)  # 1-5的难度级别
        self.max_samples = kwargs.get('max_samples', None)
        
        # 定义默认提示模板，使用双花括号语法确保与get_prompt方法兼容
        self.default_template = kwargs.get('template', 
            "问题: {{problem}}\n\n请一步步解答这个数学问题，最后给出答案。"
        )
        
        # 定义相对路径和默认数据目录
        self.demo_data_url = 'https://raw.githubusercontent.com/hendrycks/math/master/MATH/demo.jsonl'
        
        # 检查是否提供了数据路径，如果没有则设置默认值
        if not self.data_path:
            # 尝试多个可能的本地数据路径
            possible_paths = [
                # 相对于当前工作目录
                os.path.join("data", "math"),
                # 相对于项目根目录
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "math"),
                # 相对于用户home目录
                os.path.join(os.path.expanduser("~"), "model_evaluate_demo", "data", "math"),
                # 相对于用户home目录
                os.path.join(os.path.expanduser("~"), "data", "math")
            ]
            
            # 选择第一个存在的路径
            for path in possible_paths:
                if os.path.exists(path):
                    self.data_path = path
                    break
                    
        print(f"MATH数据集路径: {self.data_path if self.data_path else '未设置'}")
        
    def load(self):
        """加载Math数据集"""
        cache_key = f"math_{self.subject or 'all'}_{self.difficulty or 'all'}_{self.split}"
        
        # 尝试从缓存加载
        cached_data = self.load_from_cache(cache_key)
        if cached_data is not None:
            self.data = cached_data
            print(f"从缓存加载了 {len(cached_data)} 个MATH样本")
            return self
            
        # 首先检查是否有samples.jsonl文件
        if self.data_path:
            samples_file = os.path.join(self.data_path, "samples.jsonl")
            if os.path.exists(samples_file):
                print(f"从本地文件加载MATH样本数据: {samples_file}")
                return self._load_local_jsonl(samples_file)
        
        # 其次检查是否有demo.jsonl文件
        local_demo_file = None
        if self.data_path:
            local_demo_file = os.path.join(self.data_path, "demo.jsonl")
            
        # 如果有本地demo.jsonl文件，优先使用
        if local_demo_file and os.path.exists(local_demo_file):
            print(f"从本地文件加载MATH示例数据: {local_demo_file}")
            return self._load_local_jsonl(local_demo_file)
        
        # 如果指定了本地数据路径且该路径存在
        if self.data_path and os.path.exists(self.data_path):
            # 检查dataset.jsonl
            dataset_file = os.path.join(self.data_path, "dataset.jsonl")
            if os.path.exists(dataset_file):
                print(f"从本地文件加载MATH数据集: {dataset_file}")
                return self._load_local_jsonl(dataset_file)
                
            print(f"从本地目录加载MATH数据: {self.data_path}")
            return self._load_from_local()
        
        # 否则尝试下载示例数据
        print("找不到本地MATH数据，尝试从网络下载示例数据...")
        return self._load_demo_data()
    
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
                            # 处理不同格式的数据
                            if 'problem' in item:
                                subject = item.get('type', item.get('subject', 'unknown'))
                                difficulty = item.get('level', item.get('difficulty', 1))
                                processed_item = self._process_item(item, subject, difficulty)
                                
                                # 如果item中已经有answer字段，直接使用
                                if 'answer' in item and not processed_item.get('answer'):
                                    processed_item['answer'] = item['answer']
                                
                                data.append(processed_item)
                        except json.JSONDecodeError:
                            print(f"跳过无效的JSON行: {line[:50]}...")
            
            self.data = data
            
            # 保存到缓存
            cache_key = f"math_local_{os.path.basename(file_path)}_{self.split}"
            self.save_to_cache(cache_key, data)
            
            print(f"从本地JSONL文件加载了 {len(data)} 个MATH样本")
            return self
            
        except Exception as e:
            print(f"从本地JSONL文件加载MATH数据失败: {str(e)}")
            # 回退到创建测试数据
            print("创建测试数据作为备用...")
            self.data = self._create_test_data()
            return self
    
    def _load_from_local(self):
        """从本地目录加载数据"""
        try:
            data = []
            
            # 如果指定了学科，则只加载该学科的数据
            if self.subject:
                subject_dir = os.path.join(self.data_path, self.subject)
                if not os.path.exists(subject_dir):
                    raise FileNotFoundError(f"找不到学科目录: {subject_dir}")
                subject_dirs = [subject_dir]
            else:
                # 加载所有学科
                subject_dirs = []
                for item in os.listdir(self.data_path):
                    item_path = os.path.join(self.data_path, item)
                    if os.path.isdir(item_path) and not item.startswith('.'):
                        subject_dirs.append(item_path)
            
            # 从每个学科目录加载数据
            for subject_dir in subject_dirs:
                subject_name = os.path.basename(subject_dir)
                
                # 处理难度过滤
                if self.difficulty:
                    difficulty_dirs = [os.path.join(subject_dir, f"level{self.difficulty}")]
                else:
                    difficulty_dirs = []
                    for i in range(1, 6):  # 难度级别1-5
                        difficulty_dir = os.path.join(subject_dir, f"level{i}")
                        if os.path.exists(difficulty_dir):
                            difficulty_dirs.append(difficulty_dir)
                
                # 从每个难度级别加载数据
                for difficulty_dir in difficulty_dirs:
                    if not os.path.exists(difficulty_dir):
                        continue
                        
                    difficulty_level = int(os.path.basename(difficulty_dir).replace('level', ''))
                    
                    # 查找所有JSON文件
                    for filename in os.listdir(difficulty_dir):
                        if filename.endswith('.json'):
                            file_path = os.path.join(difficulty_dir, filename)
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    item = json.load(f)
                                    processed_item = self._process_item(item, subject_name, difficulty_level)
                                    data.append(processed_item)
                            except json.JSONDecodeError:
                                print(f"跳过无效的JSON文件: {file_path}")
            
            # 如果没有找到任何数据，尝试直接查找并加载JSON和JSONL文件
            if not data:
                print("在标准目录结构中找不到数据，尝试直接加载JSON/JSONL文件...")
                for item in os.listdir(self.data_path):
                    if item.endswith('.json') or item.endswith('.jsonl'):
                        file_path = os.path.join(self.data_path, item)
                        try:
                            if item.endswith('.jsonl'):
                                # 加载JSONL文件
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    for line in f:
                                        if line.strip():
                                            item_data = json.loads(line.strip())
                                            subject = item_data.get('type', item_data.get('subject', 'unknown'))
                                            difficulty = item_data.get('level', item_data.get('difficulty', 1))
                                            processed_item = self._process_item(item_data, subject, difficulty)
                                            data.append(processed_item)
                            else:
                                # 加载普通JSON文件
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    items = json.load(f)
                                    if isinstance(items, list):
                                        for item_data in items:
                                            subject = item_data.get('type', item_data.get('subject', 'unknown'))
                                            difficulty = item_data.get('level', item_data.get('difficulty', 1))
                                            processed_item = self._process_item(item_data, subject, difficulty)
                                            data.append(processed_item)
                                    else:
                                        subject = items.get('type', items.get('subject', 'unknown'))
                                        difficulty = items.get('level', items.get('difficulty', 1))
                                        processed_item = self._process_item(items, subject, difficulty)
                                        data.append(processed_item)
                        except Exception as e:
                            print(f"加载文件 {file_path} 时出错: {str(e)}")
            
            # 仍然没有数据，则创建示例数据
            if not data:
                print("在本地目录中找不到任何有效数据，创建测试数据...")
                data = self._create_test_data()
            
            # 处理最大样本数限制
            if self.max_samples and len(data) > self.max_samples:
                # 随机采样
                import random
                random.shuffle(data)
                data = data[:self.max_samples]
                
            self.data = data
            
            # 保存到缓存
            cache_key = f"math_{self.subject or 'all'}_{self.difficulty or 'all'}_{self.split}"
            self.save_to_cache(cache_key, data)
            
            print(f"从本地加载了 {len(data)} 个MATH样本")
            return self
            
        except Exception as e:
            print(f"从本地加载MATH数据集失败: {str(e)}")
            # 创建测试数据作为备用
            print("创建测试数据作为备用...")
            self.data = self._create_test_data()
            return self
    
    def _load_demo_data(self):
        """从URL加载示例数据"""
        try:
            print(f"从URL下载MATH示例数据: {self.demo_data_url}")
            
            response = requests.get(self.demo_data_url)
            response.raise_for_status()
            
            data = []
            for line in response.text.splitlines():
                if line.strip():
                    item = json.loads(line.strip())
                    # 由于示例数据可能没有主题和难度信息，设置为默认值
                    processed_item = self._process_item(
                        item, 
                        subject=item.get('subject', item.get('type', 'unknown')),
                        difficulty=item.get('level', item.get('difficulty', 0))
                    )
                    data.append(processed_item)
            
            if self.max_samples and len(data) > self.max_samples:
                data = data[:self.max_samples]
                
            self.data = data
            
            # 保存到缓存
            cache_key = f"math_demo_{self.split}"
            self.save_to_cache(cache_key, data)
            
            print(f"从URL加载了 {len(data)} 个MATH示例样本")
            return self
            
        except Exception as e:
            print(f"加载MATH示例数据失败: {str(e)}")
            
            # 如果无法加载在线数据，创建一些测试数据
            print("创建测试数据作为备用...")
            self.data = self._create_test_data()
            return self
    
    def _process_item(self, item, subject, difficulty):
        """处理原始数据项"""
        processed = {
            'problem': item.get('problem', ''),
            'solution': item.get('solution', ''),
            'subject': subject,
            'difficulty': difficulty
        }
        
        # 如果有现成的答案字段，直接使用
        if 'answer' in item:
            processed['answer'] = item['answer']
        else:
            # 否则尝试从解答中提取
            final_answer = self._extract_final_answer(item.get('solution', ''))
            processed['answer'] = final_answer
        
        return processed
    
    def _extract_final_answer(self, solution_text):
        """从解答文本中提取最终答案"""
        try:
            # 尝试提取"the answer is"或"= "后的内容
            import re
            
            # 尝试找 "the answer is X" 或 "answer: X"
            answer_patterns = [
                r"the\s+answer\s+is\s+([\d\.\-\+\/\(\)x]+)",
                r"answer\s*:\s*([\d\.\-\+\/\(\)x]+)",
                r"答案\s*[为是:：]\s*([\d\.\-\+\/\(\)x]+)"
            ]
            
            for pattern in answer_patterns:
                matches = re.search(pattern, solution_text.lower())
                if matches:
                    return matches.group(1).strip()
            
            # 尝试找最后的 "= X"
            equals_matches = re.findall(r"=\s*([\d\.\-\+\/\(\)x]+)", solution_text)
            if equals_matches:
                return equals_matches[-1].strip()
                
            return "Unknown"  # 如果无法提取
            
        except Exception:
            return "Unknown"
    
    def _create_test_data(self):
        """创建测试数据"""
        test_data = [
            {
                'problem': '求解方程 x^2 - 7x + 12 = 0。',
                'solution': '设方程为 x^2 - 7x + 12 = 0\n我们可以因式分解：(x-3)(x-4) = 0\n所以 x = 3 或 x = 4\n答案是: 3, 4',
                'answer': '3, 4',
                'subject': 'algebra',
                'difficulty': 1
            },
            {
                'problem': '计算三角形面积，底边长为6，高为4。',
                'solution': '三角形面积 = (底边长 × 高) / 2 = (6 × 4) / 2 = 12\n答案是: 12',
                'answer': '12',
                'subject': 'geometry',
                'difficulty': 1
            },
            {
                'problem': '对于函数 f(x) = 2x^3 - 3x^2 + 1，求 f\'(2)。',
                'solution': 'f(x) = 2x^3 - 3x^2 + 1\nf\'(x) = 6x^2 - 6x\nf\'(2) = 6(2)^2 - 6(2) = 6 × 4 - 12 = 24 - 12 = 12\n答案是: 12',
                'answer': '12',
                'subject': 'calculus',
                'difficulty': 2
            }
        ]
        return test_data 