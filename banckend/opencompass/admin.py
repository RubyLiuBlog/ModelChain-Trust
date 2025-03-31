from django.contrib import admin
from .models import AIModel

# @admin.register(AIModel)
# class AIModelAdmin(admin.ModelAdmin):
#     list_display = ('name', 'version', 'downloads', 'updated_at', 'author')
#     list_filter = ('framework', 'created_at', 'updated_at')
#     search_fields = ('name', 'description', 'author', 'tags')
#     readonly_fields = ('downloads', 'created_at', 'updated_at')
#     fieldsets = (
#         ('基本信息', {
#             'fields': ('name', 'version', 'description', 'author')
#         }),
#         ('模型详情', {
#             'fields': ('readme', 'model_size', 'framework', 'license', 'tags')
#         }),
#         ('统计信息', {
#             'fields': ('downloads', 'created_at', 'updated_at')
#         }),
#     )
