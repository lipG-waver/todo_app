#!/bin/bash

# 设置完整的环境变量
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export PATH="/Users/zhoujiashu/Desktop/ENTER/bin:$PATH"

# 激活conda环境 - 更完整的方式
source /Users/zhoujiashu/Desktop/ENTER/etc/profile.d/conda.sh
conda activate todo-env

# 确认环境
echo "PATH: $PATH" >> /tmp/todo_out.log
echo "Python path: $(which python)" >> /tmp/todo_out.log
echo "Current conda env: $CONDA_DEFAULT_ENV" >> /tmp/todo_out.log

# 启动程序
echo "Launching main.py..." >> /tmp/todo_out.log
cd /Users/zhoujiashu/Desktop/todo_app
python main.py >> /tmp/todo_out.log 2>&1