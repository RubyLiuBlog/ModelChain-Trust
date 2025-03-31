// 定期刷新任务状态
document.addEventListener('DOMContentLoaded', function() {
    // 获取任务ID
    const taskIdElement = document.getElementById('task-id');
    if (taskIdElement) {
        const taskId = taskIdElement.textContent.trim();
        
        // 如果有任务ID，则定期刷新状态
        if (taskId) {
            // 立即更新一次
            updateTaskStatus(taskId);
            
            // 每5秒更新一次状态
            setInterval(function() {
                updateTaskStatus(taskId);
            }, 5000);
        }
    }
    
    // 首页任务列表自动刷新
    const tasksList = document.getElementById('tasksList');
    if (tasksList) {
        // 每10秒刷新一次任务列表
        setInterval(function() {
            refreshTasksList();
        }, 10000);
    }
});

// 更新任务状态
function updateTaskStatus(taskId) {
    fetch(`/api/tasks/${taskId}`)
        .then(response => response.json())
        .then(data => {
            // 更新状态和上次更新时间
            const statusElement = document.getElementById('task-status');
            const updatedAtElement = document.getElementById('task-updated-at');
            
            if (statusElement) {
                // 更新状态
                statusElement.textContent = getStatusText(data.status);
                
                // 更新状态类
                statusElement.className = '';
                statusElement.classList.add('badge');
                statusElement.classList.add(getStatusClass(data.status));
            }
            
            if (updatedAtElement) {
                updatedAtElement.textContent = data.updated_at;
            }
            
            // 如果任务已完成，显示结果
            if (data.status === 'completed' && data.result && data.result.result_files && data.result.result_files.length > 0) {
                const resultContainer = document.getElementById('result-container');
                const resultFiles = document.getElementById('result-files');
                
                if (resultContainer && resultFiles) {
                    // 显示结果区域
                    resultContainer.style.display = 'block';
                    
                    // 清空现有的结果文件
                    resultFiles.innerHTML = '';
                    
                    // 添加结果文件链接
                    data.result.result_files.forEach(file => {
                        const li = document.createElement('li');
                        const a = document.createElement('a');
                        a.href = `/results/${file}`;
                        a.textContent = file;
                        a.target = '_blank';
                        li.appendChild(a);
                        resultFiles.appendChild(li);
                    });
                }
                
                // 隐藏错误容器（如果存在）
                const errorContainer = document.getElementById('error-container');
                if (errorContainer) {
                    errorContainer.style.display = 'none';
                }
                
                // 停止自动刷新
                clearInterval(window.taskUpdateInterval);
            } else if (data.status === 'failed' && data.result) {
                // 显示错误信息
                const errorContainer = document.getElementById('error-container');
                const errorMessage = document.getElementById('error-message');
                
                if (errorContainer && errorMessage) {
                    errorContainer.style.display = 'block';
                    errorMessage.textContent = data.result.error || '未知错误';
                    
                    // 添加折叠面板事件监听器
                    var coll = document.getElementsByClassName("collapsible");
                    for (var i = 0; i < coll.length; i++) {
                        coll[i].addEventListener("click", function() {
                            this.classList.toggle("active");
                            var content = this.nextElementSibling;
                            if (content.style.maxHeight) {
                                content.style.maxHeight = null;
                            } else {
                                content.style.maxHeight = content.scrollHeight + "px";
                            }
                        });
                    }
                }
                
                // 隐藏结果容器（如果存在）
                const resultContainer = document.getElementById('result-container');
                if (resultContainer) {
                    resultContainer.style.display = 'none';
                }
                
                // 停止自动刷新
                clearInterval(window.taskUpdateInterval);
            }
        })
        .catch(error => {
            console.error('获取任务状态失败:', error);
        });
}

// 刷新任务列表
function refreshTasksList() {
    fetch('/api/tasks')
        .then(response => response.json())
        .then(data => {
            // 获取任务列表表格
            const tasksList = document.getElementById('tasksList');
            
            if (tasksList && data.tasks) {
                // 清空现有的行
                tasksList.innerHTML = '';
                
                // 添加新的行
                data.tasks.forEach(task => {
                    const tr = document.createElement('tr');
                    
                    // 任务ID
                    const tdId = document.createElement('td');
                    tdId.textContent = task.id.substring(0, 8) + '...';
                    tr.appendChild(tdId);
                    
                    // 模型名称
                    const tdModel = document.createElement('td');
                    tdModel.textContent = task.model_path.split('/').pop();
                    tr.appendChild(tdModel);
                    
                    // 数据集
                    const tdDataset = document.createElement('td');
                    tdDataset.textContent = task.datasets.join(', ');
                    tr.appendChild(tdDataset);
                    
                    // 状态
                    const tdStatus = document.createElement('td');
                    const statusBadge = document.createElement('span');
                    statusBadge.textContent = getStatusText(task.status);
                    statusBadge.classList.add('badge');
                    statusBadge.classList.add(getStatusClass(task.status));
                    tdStatus.appendChild(statusBadge);
                    tr.appendChild(tdStatus);
                    
                    // 操作
                    const tdAction = document.createElement('td');
                    const viewButton = document.createElement('a');
                    viewButton.href = `/tasks/${task.id}`;
                    viewButton.classList.add('btn', 'btn-sm', 'btn-primary');
                    viewButton.textContent = '查看';
                    tdAction.appendChild(viewButton);
                    tr.appendChild(tdAction);
                    
                    tasksList.appendChild(tr);
                });
            }
        })
        .catch(error => {
            console.error('刷新任务列表失败:', error);
        });
}

// 获取状态文本
function getStatusText(status) {
    switch (status) {
        case 'pending':
            return '等待中';
        case 'running':
            return '运行中';
        case 'completed':
            return '已完成';
        case 'failed':
            return '失败';
        default:
            return '未知';
    }
}

// 获取状态类
function getStatusClass(status) {
    switch (status) {
        case 'pending':
            return 'badge-warning';
        case 'running':
            return 'badge-primary';
        case 'completed':
            return 'badge-success';
        case 'failed':
            return 'badge-danger';
        default:
            return 'badge-secondary';
    }
} 