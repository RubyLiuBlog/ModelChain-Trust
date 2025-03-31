"""
准确率评估指标实现
"""
import re
import string
from model_evaluate_demo.utils.registry import METRICS
from model_evaluate_demo.metrics.base import BaseMetric


@METRICS.register('accuracy')
class AccuracyMetric(BaseMetric):
    """
    准确率评估指标
    
    从生成文本中提取数值答案，并与参考答案比较。
    """
    def __init__(self):
        super().__init__('accuracy')
        
    def compute(self, predictions, references, **kwargs):
        """
        计算准确率
        
        Args:
            predictions: 模型生成的文本列表
            references: 参考答案列表
            **kwargs: 
                - answer_pattern: 从生成文本中提取答案的正则表达式模式
                - normalize: 是否对答案进行归一化处理
                - debug: 是否输出调试信息
                
        Returns:
            dict: 包含准确率和详细信息的字典
        """
        if len(predictions) != len(references):
            raise ValueError(f"预测数量 ({len(predictions)}) 与参考答案数量 ({len(references)}) 不匹配")
        
        answer_pattern = kwargs.get('answer_pattern', None)
        normalize = kwargs.get('normalize', True)
        debug = kwargs.get('debug', False)
        
        if debug:
            print("开始准确率计算...")
        
        # 提取预测答案
        extracted_predictions = []
        for i, pred in enumerate(predictions):
            extracted = self._extract_answer(pred, answer_pattern)
            if normalize:
                extracted = self._normalize_answer(extracted)
                
            if debug:
                print(f"样本 {i}:")
                print(f"  原始生成: {pred[:200]}..." if len(pred) > 200 else f"  原始生成: {pred}")
                print(f"  提取答案: '{extracted}'")
                
            extracted_predictions.append(extracted)
        
        # 归一化参考答案
        normalized_references = []
        for i, ref in enumerate(references):
            norm_ref = ref
            if normalize:
                norm_ref = self._normalize_answer(ref)
                
            if debug:
                print(f"样本 {i} 参考答案: '{ref}' -> 归一化: '{norm_ref}'")
                
            normalized_references.append(norm_ref)
        
        # 计算准确率
        correct = 0
        details = []
        
        for i, (pred, ref) in enumerate(zip(extracted_predictions, normalized_references)):
            # 使用强化的答案匹配逻辑
            is_correct = self._is_answer_correct(pred, ref)
            
            if is_correct:
                correct += 1
                
            details.append({
                'index': i,
                'prediction': predictions[i],
                'extracted': extracted_predictions[i],
                'reference': references[i],
                'normalized_reference': normalized_references[i],
                'correct': is_correct
            })
            
            if debug:
                print(f"样本 {i} 判断: {'✓ 正确' if is_correct else '✗ 错误'}")
        
        accuracy = correct / len(predictions) if predictions else 0
        
        if debug:
            print(f"准确率计算完成: {correct}/{len(predictions)} = {accuracy}")
        
        return {
            'score': accuracy,
            'correct': correct,
            'total': len(predictions),
            'details': details
        }
    
    def _is_answer_correct(self, prediction, reference):
        """
        判断预测答案是否正确
        
        Args:
            prediction: 归一化后的预测答案
            reference: 归一化后的参考答案
            
        Returns:
            bool: 是否正确
        """
        # 1. 精确匹配
        if prediction == reference:
            return True
            
        # 2. 数值匹配（允许精度误差）
        try:
            # 替换常见的数学符号
            pred_processed = prediction.replace('π', 'pi').replace('pi', '3.14159')
            ref_processed = reference.replace('π', 'pi').replace('pi', '3.14159')
            
            # 尝试转换为浮点数
            pred_num = float(pred_processed)
            ref_num = float(ref_processed)
            
            # 允许小误差，处理浮点精度问题
            if abs(pred_num - ref_num) < 1e-5:
                return True
                
            # 对于大数，考虑相对误差
            if max(abs(pred_num), abs(ref_num)) > 1.0:
                relative_error = abs(pred_num - ref_num) / max(abs(pred_num), abs(ref_num))
                if relative_error < 0.001:  # 允许0.1%的相对误差
                    return True
        except (ValueError, TypeError):
            pass  # 不是数值，继续下一步判断
            
        # 3. 集合匹配（顺序无关）
        # 如果答案包含逗号，可能是一组值
        if (',' in prediction and ',' in reference) or (';' in prediction and ';' in reference):
            # 提取数组元素
            pred_items = re.split(r'[,;\s]+', prediction)
            ref_items = re.split(r'[,;\s]+', reference)
            
            # 移除空元素
            pred_items = [item.strip() for item in pred_items if item.strip()]
            ref_items = [item.strip() for item in ref_items if item.strip()]
            
            # 转换为集合进行比较
            return set(pred_items) == set(ref_items)
            
        # 4. 包含关系检查（适用于较长文本答案）
        if len(prediction) > 10 and len(reference) > 10:
            # 检查核心内容是否包含
            pred_tokens = set(re.findall(r'\b\w+\b', prediction.lower()))
            ref_tokens = set(re.findall(r'\b\w+\b', reference.lower()))
            
            # 如果共同词占参考答案词的80%以上，认为基本正确
            if len(ref_tokens) > 0:
                common_ratio = len(pred_tokens.intersection(ref_tokens)) / len(ref_tokens)
                if common_ratio > 0.8:
                    return True
        
        return False
    
    def _extract_answer(self, text, pattern=None):
        """
        从文本中提取答案
        
        参考了OpenCompass等主流评测框架的实现
        """
        if not text:
            return ""
            
        # 如果提供了模式，使用该模式
        if pattern:
            matches = re.search(pattern, text)
            if matches and matches.groups():
                return matches.group(1).strip()
        
        # 尝试查找boxed答案 (常见于LaTeX格式)
        boxed_pattern = r'\\boxed\{(.*?)\}'
        boxed_matches = re.search(boxed_pattern, text)
        if boxed_matches:
            return boxed_matches.group(1).strip()
        
        # 1. 查找直接的答案标识词
        direct_patterns = [
            # 中文模式
            r'答案是[:：]?\s*(.+?)(?:\.|。|$|\n)',
            r'答案[:：]\s*(.+?)(?:\.|。|$|\n)',
            r'答案为[:：]?\s*(.+?)(?:\.|。|$|\n)',
            r'因此答案为:?\s*(.+?)(?:\.|。|$|\n)',
            r'所以答案是:?\s*(.+?)(?:\.|。|$|\n)',
            r'因此答案是:?\s*(.+?)(?:\.|。|$|\n)',
            r'所以答案为:?\s*(.+?)(?:\.|。|$|\n)',
            r'最终答案:?\s*(.+?)(?:\.|。|$|\n)',
            r'最终答案为:?\s*(.+?)(?:\.|。|$|\n)',
            r'最终答案是:?\s*(.+?)(?:\.|。|$|\n)',
            r'计算得[\s\S]*答案[是为]?\s*[:：]?\s*(.+?)(?:\.|。|$|\n)',
            
            # 英文模式
            r'the answer is:?\s*(.+?)(?:\.|$|\n)',
            r'answer:?\s*(.+?)(?:\.|$|\n)',
            r'the final answer is:?\s*(.+?)(?:\.|$|\n)',
            r'therefore,? the answer is:?\s*(.+?)(?:\.|$|\n)',
            r'thus,? the answer is:?\s*(.+?)(?:\.|$|\n)',
            r'hence,? the answer is:?\s*(.+?)(?:\.|$|\n)',
            r'so,? the answer is:?\s*(.+?)(?:\.|$|\n)'
        ]
        
        for p in direct_patterns:
            matches = re.search(p, text, re.IGNORECASE)
            if matches:
                return matches.group(1).strip()
        
        # 2. 检查Python代码输出
        code_patterns = [
            r'```(?:python|)\s*[\s\S]*?```\s*输出[:：]?\s*(.+?)(?:\n|$)',
            r'```output\s*\n([\d\.\+\-]+)',
            r'执行结果[:：]?\s*(.+?)(?:\n|$)'
        ]
        
        for p in code_patterns:
            matches = re.search(p, text)
            if matches:
                return matches.group(1).strip()
        
        # 3. 查找等式结果
        equals_pattern = r'=\s*([\d\.\+\-πpi\/\*]+)(?:\s|$|\.|。|,|，)'
        equals_matches = re.findall(equals_pattern, text)
        if equals_matches:
            # 返回最后一个等式结果
            return equals_matches[-1].strip()
        
        # 4. 提取数值答案
        number_patterns = [
            r'得[到得][\s\S]{0,10}([\d\.]+)(?:\s|$|\.|。)',
            r'计算得[到得][\s\S]{0,10}([\d\.]+)(?:\s|$|\.|。)',
            r'结果[为是][\s\S]{0,10}([\d\.]+)(?:\s|$|\.|。)',
            r'(?:等于|=)[\s\S]{0,5}([\d\.]+)(?:\s|$|\.|。)'
        ]
        
        for p in number_patterns:
            matches = re.search(p, text)
            if matches:
                return matches.group(1).strip()
        
        # 5. 尝试从最后一段提取
        paragraphs = text.split('\n\n')
        last_paragraph = paragraphs[-1].strip() if paragraphs else ""
        
        # 如果最后一段比较短，可能是答案总结
        if last_paragraph and len(last_paragraph) < 100:
            # 尝试查找数字或结论性质的表述
            conclusion_matches = re.search(r'(?:因此|所以|综上|总之)[\s\S]{0,20}([\d\.]+|[\u4e00-\u9fa5]{2,10})(?:\.|。|$)', last_paragraph)
            if conclusion_matches:
                return conclusion_matches.group(1).strip()
                
            # 如果是非常短的段落（可能就是答案本身）
            if len(last_paragraph) < 30 and not re.search(r'(?:问题|题目|解|思路|分析)', last_paragraph):
                return last_paragraph
        
        # 6. 从最后一行尝试提取答案
        lines = text.strip().split('\n')
        last_line = lines[-1].strip() if lines else ""
        
        # 如果最后一行有明确的"所以"、"因此"等结论性词语
        conclusion_matches = re.search(r'(?:所以|因此|综上|总之)[\s\S]*?([\d\.]+|[\u4e00-\u9fa5]{2,10})(?:\.|。|$)', last_line)
        if conclusion_matches:
            return conclusion_matches.group(1).strip()
        
        # 如果最后一行是数字，可能是答案
        last_line_numbers = re.findall(r'[-+]?[\d\.]+(?:π|pi)?', last_line)
        if last_line_numbers:
            return last_line_numbers[-1]
            
        # 7. 如果文本非常短，直接返回整个文本
        if len(text) < 50 and not re.search(r'(?:问题|题目|请|我们)', text):
            return text.strip()
            
        # 8. 实在找不到，返回最后一行
        return last_line
    
    def _normalize_answer(self, answer):
        """
        归一化答案
        
        对答案进行标准化处理，移除无关字符，统一格式
        """
        if not answer:
            return ""
            
        # 移除引号、括号和其他干扰字符
        answer = re.sub(r'[「」『』\(\)\[\]\{\}"\'""'']', '', answer)
        
        # 移除常见的单位和修饰词
        answer = re.sub(r'(?:单位|个|米|千米|公里|厘米|毫米|平方米|立方米|千克|克|吨|升|毫升|小时|分钟|秒|度|弧度|美元|元|人民币|美金|欧元|英镑|日元)', '', answer)
        
        # 替换具有相同含义的中文词语
        answer = (answer.replace('是', '')
                       .replace('约', '')
                       .replace('大约', '')
                       .replace('大概', '')
                       .replace('左右', '')
                       .replace('接近', '')
                       .replace('等于', '')
                       .replace('等于', '')
                       .replace('等于是', ''))
        
        # 转换为小写
        answer = answer.lower()
        
        # 替换多个空格为单个空格
        answer = re.sub(r'\s+', ' ', answer).strip()
        
        # 处理特殊数学表示
        answer = (answer.replace('×', '*')
                       .replace('÷', '/')
                       .replace('（', '(')
                       .replace('）', ')')
                       .replace('，', ',')
                       .replace('。', '.'))
        
        # 处理分数形式
        fraction_match = re.search(r'(\d+)/(\d+)', answer)
        if fraction_match:
            try:
                num = int(fraction_match.group(1))
                denom = int(fraction_match.group(2))
                decimal = num / denom
                # 如果能整除，使用整数形式
                if decimal.is_integer():
                    answer = str(int(decimal))
                else:
                    # 否则保留原始分数形式
                    pass
            except:
                pass
        
        # 如果完全是数值形式，尝试统一格式
        if re.match(r'^[-+]?[\d\.]+$', answer):
            try:
                # 尝试转为浮点数再转回字符串，统一格式
                num = float(answer)
                if num.is_integer():
                    # 如果是整数，移除小数点和零
                    answer = str(int(num))
                else:
                    # 浮点数，保留5位小数
                    answer = str(round(num, 5)).rstrip('0').rstrip('.')
            except:
                pass
        
        return answer 