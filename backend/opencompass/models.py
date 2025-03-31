from django.db import models

class AIModel(models.Model):
    name = models.CharField(max_length=200, unique=True, help_text="模型名称")
    address = models.CharField(max_length=42, help_text="模型地址")  # ETH地址长度为42（包含'0x'前缀）

    class Meta:
        ordering = ['-id']
        verbose_name = "AI模型"
        verbose_name_plural = "AI模型"

    def __str__(self):
        return f"{self.name} ({self.address})"

class ce_model(models.Model):
    name = models.CharField(max_length=200, unique=True, help_text="模型名称")

    class Meta:
        ordering = ['-id']
        verbose_name = "CE模型"
        verbose_name_plural = "CE模型"

    def __str__(self):
        return self.name
    
class ce_type(models.Model):
    name = models.CharField(max_length=200, unique=True, help_text="类型名称")
    address = models.CharField(max_length=42, help_text="类型地址")  # ETH地址长度为42（包含'0x'前缀）
    type = models.CharField(max_length=42, help_text="数据类型")
    class Meta:
        ordering = ['-id']
        verbose_name = "CE类型"
        verbose_name_plural = "CE类型"

    def __str__(self):
        return f"{self.name} ({self.address})"
