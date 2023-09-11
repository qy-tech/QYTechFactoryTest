#!/bin/bash

# 作者：Jax
# 创建时间：2023-09-11
# 当前版本：V1.0

# 描述:
#   此脚本用于持续监测HDMI连接状态并输出到标准输出。

# 参数说明:
#   无需提供任何参数。
echo "FactoryTest HDMI started"

while true; do
    # 使用cat命令读取HDMI连接状态并输出到标准输出
    cat /sys/class/drm/card0-HDMI-A-1/status
    sleep 1
done

echo "FactoryTest HDMI finished"
