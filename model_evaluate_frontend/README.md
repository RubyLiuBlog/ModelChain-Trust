# 模型评测Web前端

一个简单的Web界面，用于调用`comprehensive_evaluation.py`进行模型评测。

## 功能特点

- 选择模型、数据集和样本数量
- 查看评测任务状态和进度
- 实时更新任务状态
- 查看评测结果详情

## 前置条件

- 已安装Python 3.8+
- 已安装Flask
- 已经配置好`model_evaluate_demo`项目

## 安装

```bash
# 安装Flask
pip install flask
```

## 运行

```bash
cd /path/to/model_evaluate_web
python app.py
```

然后在浏览器中访问 http://localhost:5000

## 使用方法

1. 在首页选择要评测的模型、数据集和样本数量
2. 点击"开始评测"按钮开始评测
3. 在任务详情页面查看评测进度
4. 评测完成后，查看评测结果

## 配置

- 模型目录：默认为`/home/bugsmith`，可以通过环境变量`MODELS_DIR`进行配置

```bash
# a设置模型目录
export MODELS_DIR=/path/to/models
python app.py
```

## 目录结构

```
model_evaluate_web/
├── app.py                # 应用主文件
├── static/
│   ├── css/
│   │   └── style.css     # 样式文件
│   └── js/
│       └── main.js       # JavaScript文件
└── templates/
    ├── index.html        # 首页模板
    ├── task.html         # 任务状态页面模板
    ├── results.html      # 结果查看页面模板
    └── error.html        # 错误页面模板
```

## 与模型评测框架的集成

此Web前端通过调用`model_evaluate_demo/comprehensive_evaluation.py`脚本与模型评测框架集成。评测任务在后台线程中运行，结果保存在`./outputs`目录中。

要查看评测结果，请在任务完成后点击任务详情页面中的结果文件链接。

## 贡献

欢迎提出建议和改进意见！ 