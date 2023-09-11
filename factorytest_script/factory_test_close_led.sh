#!/bin/bash

# 作者：Jax
# 创建时间：2023-09-11
# 当前版本：V1.0

# 描述:
#   此脚本用于关闭LED灯, 测试时所有的灯同时灭。

# 参数说明:
#   无需提供任何参数。
echo "FactoryTest close led started"

# 定义LED和GPIO路径的数组
led_paths=(
    "/sys/class/leds/led_1/brightness"
    "/sys/class/leds/led_2/brightness"
    "/sys/class/leds/led_3/brightness"
    "/sys/class/leds/led_4/brightness"
    "/sys/class/leds/led_5/brightness"
    "/sys/class/leds/led_6/brightness"
    "/sys/class/leds/led_7/brightness"
    "/sys/class/leds/led_8/brightness"
    "/sys/class/gpio/gpio138/value"
    "/sys/class/gpio/gpio141/value"
)

# 将LED和GPIO全部设置为0
for path in "${led_paths[@]}"; do
    echo 0 >"$path"
done

echo "FactoryTest close led finished"
