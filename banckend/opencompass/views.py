from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from .models import AIModel,ce_type
import os
from django.conf import settings
import logging

# 设置日志记录器
logger = logging.getLogger(__name__)

@require_http_methods(["GET"])
def get_aimodels(request):
    """获取所有AI模型列表选项"""
    try:
        models = AIModel.objects.all().values('id', 'name')
        
        return JsonResponse({
            'success': "true",
            'data': list(models),
            'message': 'success'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': "false",
            'message': str(e)
        }, status=500)
    

@require_http_methods(["GET"])
def get_dataset(request):
    """获取所有数据集类型列表"""
    try:
        datasets = ce_type.objects.all().values('id', 'name')
        
        return JsonResponse({
            'success': "true",
            'data': list(datasets),
            'message': 'success'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': "false",
            'message': str(e)
        }, status=500)

@csrf_exempt  # 允许跨域POST请求
@require_http_methods(["POST"])
def create_test(request):
    """创建模型性能测试"""
    try:
        # 解析请求体中的JSON数据
        data = json.loads(request.body)
        model_id = data.get('modelIds')
        dataset_ids = data.get('datasetIds', [])
        
        # 验证输入参数
        if model_id is None:
            return JsonResponse({
                'success': False,
                'message': '模型ID不能为空'
            })
            
        if not dataset_ids:
            return JsonResponse({
                'success': False,
                'message': '数据集ID列表不能为空'
            })
            
        # 获取模型路径
        model_path = os.path.join(settings.MODEL_ROOT_DIR, str(model_id))
        if not os.path.exists(model_path):
            return JsonResponse({
                'success': False,
                'message': f'模型路径不存在: {model_path}'
            })

        # 从数据库获取数据集名称
        try:
            datasets = ce_type.objects.filter(id__in=dataset_ids).values_list('name', flat=True)
            if not datasets:
                return JsonResponse({
                    'success': False,
                    'message': '未找到指定的数据集'
                })
            datasets_str = ' '.join(datasets)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'获取数据集信息失败: {str(e)}'
            })

        # 构建测试命令
        test_command = (
            f"python model_evaluate_demo/comprehensive_evaluation.py "
            f"--model-path={model_path} "
            f"--datasets {datasets_str} "
            f"--max-samples=5 "
            f"--debug"
        )
        
        # 设置工作目录
        work_dir = "E:/yun_test"
        if not os.path.exists(work_dir):
            os.makedirs(work_dir)
            
        # 执行命令并获取输出结果
        import subprocess
        try:
            process = subprocess.Popen(
                test_command,
                shell=True,
                cwd=work_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True  # 使用文本模式而不是字节模式
            )
            
            # 获取输出和错误信息
            stdout, stderr = process.communicate()
            
            # 等待进程完成并获取返回码
            return_code = process.wait()
            
            # 准备输出结果
            execution_result = {
                'return_code': return_code,
                'stdout': stdout,
                'stderr': stderr,
                'success': return_code == 0
            }
            
            # 记录输出到日志
            if return_code == 0:
                logger.info(f"命令执行成功:\n{stdout}")
            else:
                logger.error(f"命令执行失败:\n{stderr}")
            
            return JsonResponse({
                'success': True,
                'data': {
                    'command': test_command,
                    'working_directory': work_dir,
                    'model_path': model_path,
                    'datasets': list(datasets),
                    'execution_result': execution_result
                }
            })
            
        except Exception as e:
            logger.error(f"执行测试命令失败: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'执行测试命令失败: {str(e)}'
            })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': '无效的JSON格式'
        }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)
