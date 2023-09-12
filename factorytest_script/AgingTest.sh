#!/bin/bash

# 作者：Jax
# 创建时间：2023-09-11
# 当前版本：V1.0

# 描述:
#   用于执行老化测试的脚本，测试时红绿灯交替闪烁。
#   测试成功后亮绿灯
#   测试失败后亮红灯

# 参数说明:
#   -M MEMORY_SIZE_MB 默认为512M。
#   -s TEST_DURATION_SECONDS 默认为7200s

# 定义Usage函数
usage() {
    echo "USAGE: $0 [-M MEMORY_SIZE_MB] [-T TEST_DURATION_SECONDS]"
    echo "No ARGS means use default MEMORY_SIZE_MB=512 and TEST_DURATION_SECONDS=7200"
    echo "WHERE: -M MEMORY_SIZE_MB = specify memory size in MB"
    echo "       -s TEST_DURATION_SECONDS = specify test duration in seconds"
    exit 1
}

# 文件用于判断是否需要进行老化测试
AGING_ENABLED_FILE=/aging_start_stamp

# 设置老化测试LOG文件位置
current_time=$(date +"%Y%m%d%H%M%S")
TEST_LOG_DIR=/usr/share/agingtest
TEST_LOG_AGINGTEST=$TEST_LOG_DIR/agingtest_$current_time.log
TEST_LOG_CPU=$TEST_LOG_DIR/cputest.log

echo "Start Aging Test" >"$TEST_LOG_AGINGTEST"

# 如果LOG目录不存在，则创建
if [ ! -d "$TEST_LOG_DIR" ]; then
    echo "Create agingtest log dir" >>"$TEST_LOG_AGINGTEST"
    mkdir -p $TEST_LOG_DIR
fi

# 设置默认测试参数
MEMORY_SIZE_MB=512         # 内存大小（MB）
TEST_DURATION_SECONDS=7200 # 测试持续时间（2小时）

runtime_seconds=0          # 初始化运行时间为0


# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case "$1" in
    -M)
        MEMORY_SIZE_MB="$2"
        shift 2
        ;;
    -s)
        TEST_DURATION_SECONDS="$2"
        shift 2
        ;;
    *)
        usage
        ;;
    esac
done

# LED控制命令
GREEN_LED=/sys/class/gpio/gpio138/value
RED_LED=/sys/class/gpio/gpio141/value
RC_LOCAL_FILE=/etc/rc.local


service network-manager stop

# 如果AGING_ENABLED_FILE不存在，表示老化测试被禁用，记录日志并退出
if [ ! -e "$AGING_ENABLED_FILE" ]; then
    echo "Aging Test Disabled, exit." >>"$TEST_LOG_AGINGTEST"
    exit
fi

# 启动stressapptest测试
stressapptest -M $MEMORY_SIZE_MB -s $TEST_DURATION_SECONDS -i 4 -C 4 -l $TEST_LOG_CPU >/dev/null 2>&1 &
pid_cpu_test=$!
echo "CPU test start" >>"$TEST_LOG_AGINGTEST"

# 启动LED闪烁，表示测试正在运行
while true; do
    if ps -p $pid_cpu_test >/dev/null; then
        # 计算CPU测试运行时间
        echo "CPU test is running." >>"$TEST_LOG_AGINGTEST"
        cup_test_time=$(ps -o etimes= -p "$pid_cpu_test")
        echo "CPU test runtime $cup_test_time" >>"$TEST_LOG_AGINGTEST"
        if [ -n "$cup_test_time" ]; then
            runtime_seconds=$cup_test_time
        fi
        echo 1 >$GREEN_LED
        sleep 1
        echo 0 >$GREEN_LED
        sleep 1
        echo 1 >$RED_LED
        sleep 1
        echo 0 >$RED_LED
        sleep 1
        echo "CPU test running" >>"$TEST_LOG_AGINGTEST"
    else
        echo "CPU test is exit." >>"$TEST_LOG_AGINGTEST"
        break # 进程不存在时退出循环
    fi
done

# 根据运行时间判断测试结果
if [ "$runtime_seconds" -ge $((TEST_DURATION_SECONDS - 10)) ]; then
    echo "CPU test OK" >>"$TEST_LOG_AGINGTEST"
    # 测试成功：亮绿灯
    echo 1 >$GREEN_LED
    echo 0 >$RED_LED
    rm -f $AGING_ENABLED_FILE

    echo host >/sys/devices/platform/fe8a0000.usb2-phy/otg_mode

    # 要添加到 /etc/rc.local 的命令
    otg_mode_host="echo host >/sys/devices/platform/fe8a0000.usb2-phy/otg_mode"

    # 检查是否已添加到 /etc/rc.local
    if ! grep -qF "$otg_mode_host" "$RC_LOCAL_FILE"; then
        # 使用 sed 在 /etc/rc.local 的末尾添加命令
        sed -i "\$i$otg_mode_host" "$RC_LOCAL_FILE" && echo "Command added to $RC_LOCAL_FILE"
    fi
else
    echo "CPU test Failed" >>"$TEST_LOG_AGINGTEST"
    # 测试失败：亮红灯
    echo 0 >$GREEN_LED
    echo 1 >$RED_LED
fi

