#!/bin/bash

# 文件用于判断是否需要进行老化测试
AGING_ENABLED_FILE=/aging_start_stamp

# 设置老化测试LOG文件位置
current_time=$(date +"%Y%m%d%H%M%S")
TEST_LOG_DIR=/usr/share/agingtest
TEST_LOG_AGINGTEST=$TEST_LOG_DIR/agingtest_$current_time.log
TEST_LOG_CPU=$TEST_LOG_DIR/cputest.log

# 如果LOG目录不存在，则创建
if [ ! -d "$TEST_LOG_DIR" ]; then
    echo "Create agingtest log dir"
    mkdir -p $TEST_LOG_DIR
fi

# 设置测试参数
MEMORY_SIZE_MB=512         # 内存大小（MB）
TEST_DURATION_SECONDS=7200 # 测试持续时间（2小时）

# LED控制命令
GREEN_LED=/sys/class/gpio/gpio138/value
RED_LED=/sys/class/gpio/gpio141/value

echo "Start Aging Test" >"$TEST_LOG_AGINGTEST"

# 如果AGING_ENABLED_FILE不存在，表示老化测试被禁用，记录日志并退出
if [ ! -e "$AGING_ENABLED_FILE" ]; then
    echo "Aging Test Disable, exit." >>"$TEST_LOG_AGINGTEST"
    exit
fi

# 启动stressapptest测试
stressapptest -M $MEMORY_SIZE_MB -s $TEST_DURATION_SECONDS -i 4 -C 4 -l $TEST_LOG_CPU >/dev/null 2>&1 &
pid_cpu_test=$!
echo "CPU test start" >>"$TEST_LOG_AGINGTEST"

# 启动LED闪烁，表示测试正在运行
while true; do
    if ps -p $pid_cpu_test >/dev/null; then
        echo "CPU test is running." >>"$TEST_LOG_AGINGTEST"
        echo 1 >$GREEN_LED
        sleep 1
        echo 0 >$GREEN_LED
        sleep 1
        echo "CPU test running" >>"$TEST_LOG_AGINGTEST"
    else
        echo "CPU test is exit." >>"$TEST_LOG_AGINGTEST"
        break # 进程不存在时退出循环
    fi
    sleep 1 # 可以调整检查的间隔时间
done

# 计算CPU测试运行时间
runtime_seconds=$(ps -o etimes= -p "$pid_cpu_test")
echo "CPU test runtime $runtime_seconds" >>"$TEST_LOG_AGINGTEST"

# 根据运行时间判断测试结果
if [ "$runtime_seconds" -ge "$TEST_DURATION_SECONDS" ]; then
    echo "CPU test OK" >>"$TEST_LOG_AGINGTEST"
    # 测试成功：亮绿灯
    echo 1 >$GREEN_LED
    echo 0 >$RED_LED
    rm -f $AGING_ENABLED_FILE
else
    echo "CPU test Failed" >>"$TEST_LOG_AGINGTEST"
    # 测试失败：亮红灯
    echo 0 >$GREEN_LED
    echo 1 >$RED_LED
fi
