#!/bin/bash

# 作者：Jax
# 创建时间：2023-09-11
# 当前版本：V1.0

# 描述：
# 此脚本使用evtest来监视指定名称的输入设备的输入事件。

# 参数：
# $1：要监视的输入设备的名称，可以是 "Loader" 或 "Power"，不区分大小写。
echo "FactoryTest key started"

# 将输入参数转换为小写以进行不区分大小写的匹配
input_name=$(echo "$1" | tr '[:upper:]' '[:lower:]')

# 根据输入名称设置对应的设备名称
case "$input_name" in
"loader")
    device_name="gpio_keys"
    ;;
"power")
    device_name="rk805 pwrkey"
    ;;
*)
    echo "无效的输入设备名称：$1"
    exit 1
    ;;
esac

# 使用evtest来监视指定名称的输入设备的输入事件
evtest $(lsinput | grep -B 5 "name\s*:\s*\"$device_name\"" | grep "/dev/input/event" | awk '{print $1}')

echo "FactoryTest key finished"
