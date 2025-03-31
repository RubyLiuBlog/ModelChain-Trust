from django.urls import path
from . import views, wallet_views, contract_views

urlpatterns = [
    
    # 钱包相关的路由
    path('wallet/verify/', wallet_views.verify_wallet, name='verify_wallet'),
    
    # 注册模型的路由
    path('models/register-model/', contract_views.register_model, name='register_model'),
    
    # 性能报告相关的路由
    path('performance/list/', contract_views.get_performance_list, name='get_performance_list'),
    
    # AI模型相关接口
    path('models/option/', views.get_aimodels, name='get_aimodels'),
   
    # 数据集相关接口
    path('models/dataset/', views.get_dataset, name='get_dataset'),
    
    # 添加新的测试创建路由
    path('models/createtest/', views.create_test, name='create_test'),
    
    # 注册模型接口
    # path('models/register/', views.register_model, name='register_model'),
    
    # 文件上传进度查询接口
    path('models/upload-progress/', contract_views.get_upload_progress, name='get_upload_progress'),
]










