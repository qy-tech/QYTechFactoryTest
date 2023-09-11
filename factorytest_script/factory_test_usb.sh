#!/bin/bash

# 作者：Jax
# 创建时间：2023-09-11
# 当前版本：V1.0

# 描述:
#   此脚本用于执行以下操作：
#   1. 获取挂载的U盘路径。
#   2. 在U盘上创建一个测试文件。
#   3. 生成一个10MB大小的测试文件并检查是否创建成功。
#   4. 强制同步磁盘缓存以确保数据写入物理存储介质。
#   5. 从测试文件中读取数据，保存读取速度等信息，并将结果打印出来。
#   6. 删除生成的测试文件。

# 参数说明:
#   无需提供任何参数。
echo "FactoryTest usb started"

# 获取/mnt/udisk的路径
udisk_path=$(mount | grep /dev/sd | awk '{print $3}' | head -n 1)

# 检查是否为空
if [ -z "$udisk_path" ]; then
    echo "未挂载udisk到 $udisk_path"
    exit 1
fi

# 定义测试文件路径
testfile=$udisk_path/testfile

# 创建测试文件并检查是否创建成功
touch "$testfile"
if [ ! -e "$testfile" ]; then
    echo "创建测试文件 $testfile 失败"
    exit 1
fi

# 生成一个10MB大小的测试文件，并将输出重定向到/dev/null以消除输出
dd if=/dev/zero of="$testfile" bs=1M count=10 >/dev/null 2>&1

# 强制同步磁盘缓存以确保数据写入物理存储介质
sync

# 从测试文件中读取数据，并将结果保存到变量result中，同时将输出重定向到/dev/null以消除输出
result=$(dd if="$testfile" of=/dev/null bs=1M 2>&1)

# 删除生成的测试文件
rm "$testfile"

# 打印result变量的内容，通常包含读取速度等信息
echo "$result"

echo "FactoryTest usb finished"
