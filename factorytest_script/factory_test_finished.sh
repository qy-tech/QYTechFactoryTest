#!/bin/bash
# 作者：Jax
# 创建时间：2023-09-11
# 当前版本：V1.0

# 描述:
#   测试完成，
#   关闭ADB或者将老化脚本添加到开机启动

# 参数说明:
#   -A | --agingtest   启用老化测试

# 文件和目录路径

# 定义Usage函数
usage() {
    echo "使用方法："
    echo "  $0 [-A | --agingtest]"
    echo
    echo "参数说明:"
    echo "  -A | --agingtest   启用老化测试"
    exit 1
}

AGINGTEST_ENABLED=false

AGING_STAMP=/aging_start_stamp
AGING_SCRIPT_SRC=/tmp/factorytest_bin/AgingTest
AGING_SCRIPT_DEST=/usr/share/AgingTest
USB_CONFIG_SRC=/tmp/factorytest_bin/usb_config
USB_CONFIG_DEST=/usr/bin/usb_config
UDEV_RULES_SRC=/tmp/factorytest_bin/99-usb-config.rules
UDEV_RULES_DEST=/etc/udev/rules.d/99-usb-config.rules
RC_LOCAL_FILE=/etc/rc.local

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case "$1" in
    -A | --agingtest)
        AGINGTEST_ENABLED=true
        shift
        ;;
    *)
        usage
        ;;
    esac
done

# 复制老化脚本
cp "$AGING_SCRIPT_SRC" "$AGING_SCRIPT_DEST" && echo "Copied $AGING_SCRIPT_SRC to $AGING_SCRIPT_DEST"

# 复制 USB 配置脚本和 udev 规则
cp "$USB_CONFIG_SRC" "$USB_CONFIG_DEST" && cp "$UDEV_RULES_SRC" "$UDEV_RULES_DEST" && echo "Copied USB configuration files to destination"

# 授予执行权限
chmod 777 "$AGING_SCRIPT_DEST" && chmod 777 "$USB_CONFIG_DEST" && echo "Changed permissions for $AGING_SCRIPT_DEST and $USB_CONFIG_DEST"

# 同步文件系统
sync && echo "Filesystem synced"

if [[ "$AGINGTEST_ENABLED" == true ]]; then
    # 创建 aging_start_stamp 文件
    touch "$AGING_STAMP" && echo "Created $AGING_STAMP"

    # 同步文件系统
    sync && echo "Filesystem synced"

    # 要添加到 /etc/rc.local 的命令
    START_AGING_TEST="[ -f $AGING_STAMP ] && $AGING_SCRIPT_DEST"

    # 检查是否已添加到 /etc/rc.local
    if ! grep -qF "$START_AGING_TEST" "$RC_LOCAL_FILE"; then
        # 使用 sed 在 /etc/rc.local 的末尾添加命令
        sed -i "\$i$START_AGING_TEST" "$RC_LOCAL_FILE" && echo "Command added to $RC_LOCAL_FILE"
    fi

    # 同步文件系统
    sync && echo "Filesystem synced"
else

    # 要添加到 /etc/rc.local 的命令
    OTG_MODE_HOST="echo host >/sys/devices/platform/fe8a0000.usb2-phy/otg_mode"

    # 检查是否已添加到 /etc/rc.local
    if ! grep -qF "$OTG_MODE_HOST" "$RC_LOCAL_FILE"; then
        # 使用 sed 在 /etc/rc.local 的末尾添加命令
        sed -i "\$i$OTG_MODE_HOST" "$RC_LOCAL_FILE" && echo "Command added to $RC_LOCAL_FILE"
    fi

    # 同步文件系统
    sync && echo "Filesystem synced"

    echo host >/sys/devices/platform/fe8a0000.usb2-phy/otg_mode
fi

# 打印完成消息
echo "Factory Test Aging Script Configuration Completed."
