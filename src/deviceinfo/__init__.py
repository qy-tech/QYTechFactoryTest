import logging
import re

import pandas as pd
from adbutils import adb, AdbDevice

logger = logging.getLogger('root')


class DeviceInfo:
    def __init__(self):
        self.output = 'output/FactoryTestResult.csv'
        # 获取已连接的设备列表
        self.devices = []
        self.device_info = {}
        self.device: AdbDevice = None
        self.size = -1
        self.available = False
        self.update_devices()

    def update_devices(self):
        self.devices = adb.device_list()
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
        sn = re.findall(r'sn:\s+(.*?)\s+', self.device.shell('vendor_storage -R -1'), re.S)
        sn = sn[0] if sn else self.device.serial
        # 获取设备的 MAC 地址
        mac_address = self.device.shell('cat /sys/class/net/eth0/address').strip()
        # 获取设备的 CPU ID
        # cpu_id = re.findall(r'Serial(.*?)\s+', device.shell('cat /proc/cpuinfo | grep Serial'))
        cpu_id = re.findall(r'Serial\s+:\s+(\S+)', self.device.shell('cat /proc/cpuinfo'), re.S)
        cpu_id = cpu_id[0] if cpu_id else 'UNKNOWN'
        # 获取设备的 Hostname
        hostname = self.device.shell('hostname').strip()
        logger.debug(f'sn: {sn}, cpu_id: {cpu_id}, mac: {mac_address}, hostname: {hostname}')
        self.device_info = {
            'SN': sn,
            'MAC Address': mac_address,
            'CPU ID': cpu_id,
            'Hostname': hostname,
        }

    def save_device_info(self, test_result: dict):
        if self.available:
            self.device.shell('touch /aging_start_stamp && sync')
            shell_script = """
            command_to_add="[ -f /aging_start_stamp ] && stressapptest -s 14400 -i 4 -C 4 -W --stop_on_errors -M 512 & wait \$! && rm -f /aging_start_stamp"
            grep -q "$command_to_add" /etc/rc.local || (cp /etc/rc.local /etc/rc.local.backup && sed -i "/exit 0/i$command_to_add" /etc/rc.local)
            """
            self.device.shell(shell_script)
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
