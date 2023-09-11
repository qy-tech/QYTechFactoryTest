import logging
import re

import pandas as pd

from util import Adb

logger = logging.getLogger('root')


class DeviceInfo:
    def __init__(self):
        self.output = 'output/FactoryTestResult.csv'
        # 获取已连接的设备列表
        self.devices = []
        self.device_info = {}
        self.device = None
        self.size = -1
        self.available = False
        self.update_devices()

    def update_devices(self):
        self.devices = Adb.devices()
        self.size = len(self.devices)
        self.device = self.devices[0] if self.devices else None
        self.available = self.device is not None
        if self.available and not self.device_info:
            self.get_device_info()

    def get_device_info(self):
        """
        获取ADB 设备信息
        :param device:
        :return: sn, mac_address, cpu_id, hostname
        """
        # 获取设备序列号（SN）
        sn = re.findall(r'sn:\s+(.*?)\s+', Adb.shell('vendor_storage -R -1'), re.S)
        sn = sn[0] if sn else self.device[0]
        # 获取设备的 MAC 地址
        mac_address = Adb.shell('cat /sys/class/net/eth0/address').strip()
        # 获取设备的 CPU ID
        # cpu_id = re.findall(r'Serial(.*?)\s+', device.shell('cat /proc/cpuinfo | grep Serial'))
        cpu_id = re.findall(r'Serial\s+:\s+(\S+)', Adb.shell('cat /proc/cpuinfo'), re.S)
        cpu_id = cpu_id[0] if cpu_id else 'UNKNOWN'
        # 获取设备的 Hostname
        hostname = Adb.shell('hostname').strip()
        logger.debug(f'sn: {sn}, cpu_id: {cpu_id}, mac: {mac_address}, hostname: {hostname}')
        self.device_info = {
            'SN': sn,
            'MAC Address': mac_address,
            'CPU ID': cpu_id,
            'Hostname': hostname,
        }

    def save_device_info(self, test_result: dict, is_success):
        if self.available and is_success:
            self.device_info.update(test_result)
        # 读取已存在的 CSV 文件，如果文件不存在，则创建一个空的 DataFrame
        try:
            df = pd.read_csv(self.output)
        except Exception as e:
            logging.error(e)
            df = pd.DataFrame(columns=list(self.device_info.keys()))

        # 检查 CSV 文件中是否已存在相同序列号的行
        row_index = df[df['SN'] == self.device_info['SN']].index
        if not row_index.empty:
            # 更新现有行
            index = row_index[0]
            for key, value in self.device_info.items():
                df.at[index, key] = value
        else:
            # 插入新行
            # df.loc[len(df)] = new_row
            df = pd.concat([df, pd.DataFrame([self.device_info])], ignore_index=True)

        # 保存修改后的 CSV 文件
        df.to_csv(self.output, index=False)
