#!/bin/bash

# 作者：Jax
# 创建时间：2023-09-11
# 当前版本：V1.0

# 描述:
#   此脚本用于关闭所有正在运行的测试脚本

# 参数说明:
#   无需提供任何参数。

echo "Searching for factorytest processes..."
# 使用ps -ef命令获取所有进程，grep factorytest来查找与factorytest相关的进程，然后通过awk提取进程ID
pids=$(ps -ef | grep factorytest | head -n -1 | awk '{print $2}')

# 检查是否找到了相关进程
if [ -z "$pids" ]; then
    echo "No factorytest processes found."
else
    echo "Killing factorytest processes..."
    # 使用kill -9命令杀死相关进程
    kill -9 $pids
    echo "Factorytest processes killed."
fi
