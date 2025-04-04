# Generated by Django 5.1.3 on 2025-03-30 04:42

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AIModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='模型名称', max_length=200, unique=True)),
                ('address', models.CharField(help_text='模型地址', max_length=42)),
            ],
            options={
                'verbose_name': 'AI模型',
                'verbose_name_plural': 'AI模型',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='ce_model',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='模型名称', max_length=200, unique=True)),
            ],
            options={
                'verbose_name': 'CE模型',
                'verbose_name_plural': 'CE模型',
                'ordering': ['-id'],
            },
        ),
    ]
