import logging
import os.path
import re
import sys
from pathlib import Path

from PyQt6.QtCore import QProcess

logger = logging.getLogger('root')


class PyInstallerPathUtil:
    # noinspection PyProtectedMember,SpellCheckingInspection
    @staticmethod
    def get_pyinstaller_base_path():
        # 获取运行时的可执行文件路径
        path = Path(__file__)
        # 如果是PyInstaller打包的可执行文件，执行文件位于dist文件夹中
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            # 否则，使用可执行文件的目录作为基础路径
            base_path = path.parents[2].absolute()
        logger.debug(f'get_pyinstaller_base_path {base_path}')
        return base_path


class Adb:
    adb_path = os.path.join(PyInstallerPathUtil.get_pyinstaller_base_path(), 'bin', 'adb.exe')

    @staticmethod
    def shell(command):
        p = QProcess()
        p.start(Adb.adb_path, ['shell', command])
        p.waitForFinished()
        return str(p.readAllStandardOutput(), 'utf-8')

    @staticmethod
    def push(src, dest):
        p = QProcess()
        p.start(Adb.adb_path, ['push', src, dest])
        p.waitForFinished()
        return str(p.readAllStandardOutput(), 'utf-8')

    @staticmethod
    def pull(src, dest):
        p = QProcess()
        p.start(Adb.adb_path, ['pull', src, dest])
        p.waitForFinished()
        return str(p.readAllStandardOutput(), 'utf-8')

    @staticmethod
    def devices():
        # QProcessEnvironment
        # env = QProcessEnvironment::systemEnvironment();
        # env.insert("TMPDIR", "C:\\MyApp\\temp"); // Add
        # an
        # environment
        # variable
        # process.setProcessEnvironment(env);
        p = QProcess()
        p.start(Adb.adb_path, ['devices', '-l'])
        p.waitForFinished()
        output = str(p.readAllStandardOutput(), 'utf-8')
        return re.findall(r'\s+(.*?)\s+device product:(.*?)\s+model:(.*?)\s+device:(.*?)\s+transport_id:(.*?)\s+',
                          output,
                          re.I)

    @staticmethod
    def sync_test_script():
        Adb.push('factorytest_script', '/tmp')
        Adb.shell('chmod 777 -R /tmp/factorytest_script')
        Adb.shell('sync')
