from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from web3 import Web3
from datetime import datetime
import json
from .storage import ModelStorage
from django.conf import settings
import logging
import os
import uuid
import shutil
import zipfile
from .tasks import process_model_files
from enum import Enum
from django.core.cache import cache

logger = logging.getLogger(__name__)

class UploadStatus(Enum):
    QUEUED = "wait"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

# 初始化Web3连接
w3 = Web3(Web3.HTTPProvider('https://sepolia.infura.io/v3/86fa8d2d26f7440aa9ca5504cbc7e095'))

# 合约配置
CONTRACT_ADDRESS = '0x2Ce142f6A1997432F8055c135A046963F7769F55'
CONTRACT_ABI = [
    # 添加 registerModel 函数的 ABI
    {
        "inputs": [
            {"internalType": "string", "name": "_name", "type": "string"},
            {"internalType": "string", "name": "_description", "type": "string"},
            {"internalType": "string", "name": "_category", "type": "string"},
            {"internalType": "string", "name": "_ipfsHash", "type": "string"},
            {"internalType": "string", "name": "_previewHash", "type": "string"},
            {"internalType": "uint256", "name": "_price", "type": "uint256"},
            {"internalType": "enum ModelStructs.ModelLicense", "name": "_license", "type": "uint8"}
        ],
        "name": "registerModel",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getAllModels",
        "outputs": [
            {
                "internalType": "uint256[]",
                "name": "",
                "type": "uint256[]"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "_modelId", "type": "uint256"}],
        "name": "getModelDetails",
        "outputs": [
            {
                "components": [
                    {"internalType": "uint256", "name": "id", "type": "uint256"},
                    {"internalType": "address", "name": "owner", "type": "address"},
                    {"internalType": "string", "name": "name", "type": "string"},
                    {"internalType": "string", "name": "description", "type": "string"},
                    {"internalType": "string", "name": "category", "type": "string"},
                    {"internalType": "string", "name": "ipfsHash", "type": "string"},
                    {"internalType": "string", "name": "previewHash", "type": "string"},
                    {"internalType": "uint256", "name": "price", "type": "uint256"},
                    {"internalType": "bool", "name": "isPublished", "type": "bool"},
                    {"internalType": "uint8", "name": "license", "type": "uint8"}
                ],
                "internalType": "struct ModelStructs.Model",
                "name": "",
                "type": "tuple"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

@require_http_methods(["GET"])
def get_performance_list(request):
    """获取性能列表"""
    try:
        # 获取查询参数
        page_size = int(request.GET.get('pageSize', 10))
        page_num = int(request.GET.get('pageNum', 1))
        query_name = request.GET.get('queryName', '')

        test_address = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"

        if not w3.is_connected():
            raise Exception("无法连接到以太坊网络")

        contract = w3.eth.contract(
            address=Web3.to_checksum_address(CONTRACT_ADDRESS),
            abi=CONTRACT_ABI
        )

        try:
            model_ids = contract.functions.getAllModels().call({
                'from': Web3.to_checksum_address(test_address)
            })
            print(f"获取到的模型IDs: {model_ids}")

            if not model_ids:
                return JsonResponse({
                    "success": True,
                    "msg": "没有找到模型",
                    "data": {
                        "pageNumber": page_num,
                        "pageSize": page_size,
                        "record": []
                    }
                })

            records = []
            for model_id in model_ids:
                try:
                    print(f"正在获取模型ID {model_id} 的详情...")
                    model = contract.functions.getModelDetails(model_id).call({
                        'from': Web3.to_checksum_address(test_address)
                    })
                    print(f"模型 {model_id} 详情:", model)
                    
                    if query_name and query_name.lower() not in model[2].lower():  # name is at index 2
                        continue
                    
                    # 构造新的记录格式
                    record = {
                        'id': str(model[0]),  # 转换为字符串
                        'taskName': model[2],  # 使用name作为taskName
                        'models': model[4],    # 使用category作为models
                        'dataset': [
                            {
                                'id': model[5][:7],  # 使用ipfsHash的前7个字符作为id
                                'name': model[3]     # 使用description作为name
                            }
                        ],
                        'processStatus': 'wait',  # 默认状态
                        'createTime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 当前时间
                    }
                    records.append(record)
                except Exception as model_error:
                    print(f"获取模型 {model_id} 详情失败: {str(model_error)}")
                    print(f"错误类型: {type(model_error).__name__}")
                    print(f"错误详情: {str(model_error)}")
                    continue
            
            # 分页处理
            start_idx = (page_num - 1) * page_size
            end_idx = start_idx + page_size
            paginated_records = records[start_idx:end_idx]
            
            return JsonResponse({
                "success": True,
                "message": "获取性能列表成功",
                "data": {
                    "pageNumber": page_num,
                    "pageSize": page_size,
                    "record": paginated_records
                }
            })
            
        except Exception as e:
            print(f"合约调用错误: {str(e)}")
            return JsonResponse({
                "success": False,
                "msg": f"智能合约调用失败: {str(e)}",
                "data": {
                    "pageNumber": page_num,
                    "pageSize": page_size,
                    "record": []
                }
            }, status=500)
            
    except Exception as e:
        print(f"服务器错误: {str(e)}")
        return JsonResponse({
            "success": False,
            "msg": str(e),
            "data": {
                "pageNumber": page_num,
                "pageSize": page_size,
                "record": []
            }
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def register_model(request):
    """接收模型文件并加入处理队列"""
    try:
        # 获取参数
        model_files = request.FILES.get('model_files')
        readme_file = request.FILES.get('readme_file')
        address = request.POST.get('address')
        model_id = request.POST.get('modelid')
        print(model_files,readme_file,address,model_id)
        # 验证必要参数
        if not all([model_files, readme_file, address, model_id]):
            return JsonResponse({
                'success': False,
                'message': '缺少必要参数'
            }, status=400)

        # 创建临时存储目录
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp', f"{model_id}")
        os.makedirs(temp_dir, exist_ok=True)

        # 保存模型文件
        model_filename = f"{model_id}_model{os.path.splitext(model_files.name)[1]}"
        model_path = os.path.join(temp_dir, model_filename)
        with open(model_path, 'wb+') as destination:
            for chunk in model_files.chunks():
                destination.write(chunk)

        # 保存README文件
        readme_filename = f"{model_id}_readme{os.path.splitext(readme_file.name)[1]}"
        readme_path = os.path.join(temp_dir, readme_filename)
        with open(readme_path, 'wb+') as destination:
            for chunk in readme_file.chunks():
                destination.write(chunk)

        # 将任务添加到处理队列
        task = process_model_files.delay(model_path, readme_path, address, model_id)
        
        return JsonResponse({
            'success': True,
            'message': '文件上传成功，已加入处理队列',
            'data': {
                'model_id': model_id,
                'temp_model_path': model_path,
                'temp_readme_path': readme_path,
                'status': 'queued',
                'task_id': task.id  # 返回任务ID，用于前端查询进度
            }
        })

    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f"文件上传失败: {str(e)}"
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def upload_model(request):
    try:
        storage = ModelStorage()
        
        # 获取模型名称
        model_name = request.POST.get('model_name')
        if not model_name:
            return JsonResponse({
                'success': False,
                'message': '请提供模型名称'
            }, status=400)

        # 获取模型文件夹路径
        model_folder = request.POST.get('model_folder')
        if not model_folder or not os.path.exists(model_folder):
            return JsonResponse({
                'success': False,
                'message': '模型文件夹不存在'
            }, status=400)

        # 获取README文件
        readme_file = request.FILES.get('readme_file')
        if not readme_file:
            return JsonResponse({
                'success': False,
                'message': '请提供README文档'
            }, status=400)

        # 存储模型文件夹
        try:
            model_path = storage.store_model_folder(model_folder, model_name)
            logger.info(f"模型文件夹上传成功: {model_path}")
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'模型文件夹上传失败: {str(e)}'
            }, status=500)

        # 存储README文档
        try:
            readme_path = storage.store_readme(readme_file, model_name)
            logger.info(f"README文档上传成功: {readme_path}")
        except Exception as e:
            # 如果README上传失败，删除已上传的模型文件夹
            storage.delete_model(model_path)
            return JsonResponse({
                'success': False,
                'message': f'README文档上传失败: {str(e)}'
            }, status=500)

        return JsonResponse({
            'success': True,
            'data': {
                'model_path': model_path,
                'readme_path': readme_path,
                'model_url': f"{request.build_absolute_uri(settings.MEDIA_URL)}{model_path}",
                'readme_url': f"{request.build_absolute_uri(settings.MEDIA_URL)}{readme_path}"
            }
        })
        
    except Exception as e:
        logger.error(f"处理上传请求失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@require_http_methods(["GET"])
def get_task_progress(request):
    """获取任务进度"""
    task_id = request.GET.get('task_id')
    if not task_id:
        return JsonResponse({
            'success': False,
            'message': '缺少task_id参数'
        }, status=400)

    try:
        task = process_model_files.AsyncResult(task_id)
        if task.state == 'PENDING':
            response = {
                'state': 'pending',
                'current': 0,
                'total': 100,
                'status': '等待处理...'
            }
        elif task.state == 'PROGRESS':
            response = {
                'state': 'progress',
                'current': task.info.get('current', 0),
                'total': task.info.get('total', 100),
                'status': task.info.get('status', '')
            }
        elif task.state == 'SUCCESS':
            response = {
                'state': 'success',
                'current': 100,
                'total': 100,
                'status': '处理完成',
                'result': task.get()
            }
        else:
            response = {
                'state': 'error',
                'current': 0,
                'total': 100,
                'status': str(task.info)  # 这里是错误信息
            }
        
        return JsonResponse({
            'success': True,
            'data': response
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)
@csrf_exempt
@require_http_methods(["GET"])
def get_upload_progress(request):
    """获取文件上传进度"""
    try:
        model_id = request.GET.get('modelid')
        if not model_id:
            return JsonResponse({
                'success': False,
                'message': '缺少model_id参数'
            }, status=400)

        # 获取缓存的状态
        cache_key = f"upload_status_{model_id}"
        status = cache.get(cache_key, UploadStatus.QUEUED.value)

        # 检查模型目录是否存在
        model_dir = os.path.join(settings.MODEL_ROOT_DIR, model_id)
        readme_dir = os.path.join(settings.README_DIR, model_id)
        
        # 检查文件状态
        model_exists = os.path.exists(model_dir)
        readme_exists = os.path.exists(readme_dir)
        
        # 获取文件大小信息
        model_size = 0
        if model_exists:
            for root, dirs, files in os.walk(model_dir):
                model_size += sum(os.path.getsize(os.path.join(root, name)) for name in files)
        
        readme_size = 0
        if readme_exists:
            for root, dirs, files in os.walk(readme_dir):
                readme_size += sum(os.path.getsize(os.path.join(root, name)) for name in files)

        # 更新状态逻辑
        if status == UploadStatus.FAILED.value:
            current_status = UploadStatus.FAILED.value
        elif model_exists and readme_exists:
            current_status = UploadStatus.COMPLETED.value
        elif (model_exists or readme_exists) and status != UploadStatus.FAILED.value:
            current_status = UploadStatus.RUNNING.value
        else:
            current_status = UploadStatus.QUEUED.value

        # 更新缓存
        cache.set(cache_key, current_status, timeout=3600)  # 1小时过期

        return JsonResponse({
            'success': True,
            'data': {
                'model_id': model_id,
                'status': {
                    'code': current_status,
                    'model_uploaded': model_exists,
                    'readme_uploaded': readme_exists,
                    'model_size': model_size,
                    'readme_size': readme_size,
                    'progress': 100 if current_status == UploadStatus.COMPLETED.value else (
                        50 if model_exists or readme_exists else 0
                    )
                }
            }
        })

    except Exception as e:
        logger.error(f"获取上传进度失败: {str(e)}")
        # 设置失败状态
        cache_key = f"upload_status_{model_id}"
        cache.set(cache_key, UploadStatus.FAILED.value, timeout=3600)
        return JsonResponse({
            'success': False,
            'message': str(e),
            'data': {
                'status': {
                    'code': UploadStatus.FAILED.value
                }
            }
        }, status=500)




