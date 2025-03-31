# 模型评估框架 (Model Evaluate Demo)

一个轻量级的模型评估框架，支持在离线环境下对大语言模型进行标准化评估。本框架提供了一套完整的API，用于评估模型在各种数据集上的性能表现。

## 功能特点

- 支持多种数据集评估 (MATH, GSM8K等)
- 支持完全离线模式，无需网络连接
- 支持自定义提示模板
- 本地数据集加载和缓存机制
- 详细的评估结果和指标输出
- 可扩展的模型和数据集接口

## 快速开始

### 基本使用

使用`comprehensive_evaluation.py`脚本进行评估：

```bash
python model_evaluate_demo/comprehensive_evaluation.py \
  --model-path=/path/to/your/model \
  --datasets math gsm8k \
  --max-samples=5 \
  --debug
```

### 参数说明

- `--model-path`: 模型路径，指向本地HuggingFace格式的模型目录
- `--datasets`: 要评估的数据集列表，多个数据集用空格分隔
- `--max-samples`: 每个数据集最大评估样本数
- `--output-dir`: 评估结果输出目录，默认为`./outputs`
- `--device`: 使用的设备，可选值为"cuda"或"cpu"，默认自动检测
- `--debug`: 开启调试模式，显示更多信息

## 评估流程详解

1. **模型加载**: 框架会加载指定路径的模型，支持HuggingFace格式的模型
2. **数据集加载**: 框架会按照以下优先级加载数据集：
   - 缓存数据（存储在`.cache`目录下）
   - 本地samples.jsonl文件（MATH数据集）或test.jsonl文件（GSM8K数据集）
   - 本地demo.jsonl或dataset.jsonl文件
   - 本地目录结构数据
   - 在线数据（如果网络可用）
   - 内置测试数据（如果上述都失败）
3. **模板渲染**: 使用双花括号语法（如`{{problem}}`或`{{question}}`）渲染提示模板
4. **模型推理**: 对每个样本进行模型推理，生成回答
5. **结果评估**: 使用accuracy指标评估模型的表现
6. **结果保存**: 将结果保存到输出目录，包括详细结果和摘要

## 后端传参

### API接口

框架提供了`evaluate_model`API用于评估模型:

```python
from model_evaluate_demo.api import evaluate_model

results = evaluate_model(
    model_path="/path/to/your/model",
    model_type="huggingface",
    dataset_name="math",
    metrics=["accuracy"],
    max_samples=5,
    offline=True,
    trust_remote_code=True,
    local_files_only=True,
    device="cuda",
    debug=True,
    prompt_template="问题: {{problem}}\n请仔细分析并逐步解答这个数学问题。",
    generation_params={
        "temperature": 0.1,
        "max_tokens": 1024,
        "num_beams": 1
    }
)
```

### 数据集配置

评估脚本中内置了以下数据集配置：

```python
dataset_configs = {
    "gsm8k": {
        "max_samples": 100,
        "metrics": ["accuracy"],
        "generation": {
            "temperature": 0.1,
            "max_tokens": 512,
            "num_beams": 1
        },
        "prompt_template": "问题: {{question}}\n请一步步思考并给出答案。"
    },
    "math": {
        "max_samples": 50,
        "metrics": ["accuracy"],
        "generation": {
            "temperature": 0.1,
            "max_tokens": 1024,
            "num_beams": 1
        },
        "prompt_template": "问题: {{problem}}\n请仔细分析并逐步解答这个数学问题。确保你的推导过程清晰，并在最后明确给出答案。"
    }
}
```

### 模板变量说明

不同的数据集使用不同的字段名称：

- MATH数据集使用`{{problem}}`作为问题变量
- GSM8K数据集使用`{{question}}`作为问题变量

模板格式支持：
1. 双花括号语法：`{{variable}}`（推荐使用）
2. 传统format格式：`{variable}`

## 本地数据集

### 数据集位置

框架会自动搜索以下位置的数据集：

- `./data/[dataset_name]/`
- 项目根目录的`data/[dataset_name]/`
- 用户主目录下的`model_evaluate_demo/data/[dataset_name]/`
- 用户主目录下的`data/[dataset_name]/`

### 本地数据格式

#### MATH数据集

MATH数据集支持以下格式的数据：

1. samples.jsonl（优先级最高）：
```json
{"problem": "计算：\\int_0^{\\pi/2} \\sin(x)dx", "solution": "...", "answer": "1", "subject": "calculus", "level": "3"}
```

2. demo.jsonl或dataset.jsonl：
```json
{"problem": "...", "solution": "...", "answer": "...", "type": "algebra", "level": "Level 3"}
```

#### GSM8K数据集

GSM8K数据集支持以下格式的数据：

1. test.jsonl（优先级最高）：
```json
{"question": "小明有5个苹果，小红给了他3个苹果。小明现在有多少个苹果？", "answer": "小明开始有5个苹果。\n小红给了他3个苹果。\n所以小明现在有 5 + 3 = 8 个苹果。\n答案是 8。"}
```

2. 标准split文件（train.jsonl或test.jsonl）：
```json
{"question": "...", "answer": "..."}
```

## 离线模式

框架支持完全离线模式，通过设置以下环境变量：

```python
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"
```

如果使用API，可以通过参数启用离线模式：

```python
results = evaluate_model(
    model_path="...",
    offline=True,
    local_files_only=True
)
```

## 自定义评估

### 添加新的数据集

1. 创建新的数据集类，继承自`BaseDataset`：

```python
from model_evaluate_demo.utils.registry import DATASETS
from model_evaluate_demo.datasets.base import BaseDataset

@DATASETS.register('my_dataset')
class MyDataset(BaseDataset):
    def __init__(self, **kwargs):
        super().__init__('my_dataset', **kwargs)
        # 初始化特定参数
        
    def load(self):
        # 实现数据加载逻辑
        return self
```

2. 注册数据集类到`DATASETS`注册表，这已经在装饰器中实现

### 添加新的评估指标

1. 创建新的评估指标类，继承自`BaseMetric`：

```python
from model_evaluate_demo.utils.registry import METRICS
from model_evaluate_demo.metrics.base import BaseMetric

@METRICS.register('my_metric')
class MyMetric(BaseMetric):
    def __init__(self, **kwargs):
        super().__init__('my_metric', **kwargs)
        # 初始化特定参数
        
    def compute(self, predictions, references, **kwargs):
        # 实现指标计算逻辑
        return {
            'score': score,
            'details': details
        }
```

2. 注册评估指标类到`METRICS`注册表，这已经在装饰器中实现

## 输出结果

评估结果保存在以下文件中：

- `[timestamp]_[model_name]_results.json`: 详细评估结果，包含以下信息：
  - 模型路径
  - 评估的数据集
  - 硬件信息（GPU名称和内存）
  - 环境信息（transformers版本）
  - 每个数据集的评估结果（指标、耗时、样本数）
  - 每个样本的详细信息（问题、预测、参考答案、提取的预测答案、是否正确）

- `[timestamp]_[model_name]_summary.json`: 评估摘要，包含以下信息：
  - 模型路径
  - 时间戳
  - 每个数据集的准确率
  - 综合评分（如果评估多个数据集）

- `[timestamp]_api_result_*.json`: API调用结果（当使用API接口时）
