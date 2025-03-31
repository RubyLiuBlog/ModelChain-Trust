###### 1.先修改文件里面的合约地址，有两个文件，wallet和合约

###### 2.启动Django程序

进入到ModelChain，下面有manage.py
运行：

```
python manage.py runserver 9000
```

###### 3.使用多队列

  需要使用管理员安装Memurai
  然后运行：

```
celery -A open_app worker --loglevel=info -P solo
```

