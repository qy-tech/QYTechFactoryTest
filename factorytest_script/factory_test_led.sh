#!/bin/bash

# 作者：Jax
# 创建时间：2023-09-11
# 当前版本：V1.0

# 描述:
#   此脚本用于测试LED灯，所有的LED灯同时亮1s后同时灭。

# 参数说明:
#   无需提供任何参数。
echo "FactoryTest led started"

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

# 无限循环，用于持续控制LED和GPIO
while true; do
    # 将LED和GPIO全部设置为1
    for path in "${led_paths[@]}"; do
        echo 1 >"$path"
    done

    echo "leds on"
    # 等待1秒
    sleep 1

    # 将LED和GPIO全部设置为0
    for path in "${led_paths[@]}"; do
        echo 0 >"$path"
    done

    echo "leds off"
    # 等待1秒，然后再次循环
    sleep 1
done

echo "FactoryTest led finished"
