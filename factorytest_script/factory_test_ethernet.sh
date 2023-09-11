#!/bin/bash

# 作者：Jax
# 创建时间：2023-09-11
# 当前版本：V1.0

# 描述:
#   此脚本用于获取通过eth0网卡的默认网关IP地址，并执行ping测试以获取丢包率。

# 参数说明:
#   无需提供任何参数。
echo "FactoryTest ethernet started"

# 获取通过eth0网卡的默认网关IP地址
route_ip=$(ip route 2>/dev/null | awk '/via/ {print $3}')

# 如果route_ip非空，则执行以下命令
if [ -n "$route_ip" ]; then
    # 使用eth0网卡发送5个ping包到默认网关，并通过awk提取丢包率信息
    ping_result=$(ping -I eth0 -c 5 "$route_ip" | awk -F' |%' '/packet loss/ {print "loss="$6; exit}')
    echo "$ping_result"
else
    # 如果route_ip为空，表示无法获取默认网关，设置丢包率为100%
    echo "loss=100"
fi

echo "FactoryTest ethernet finished"
