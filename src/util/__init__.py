import logging
import sys
from pathlib import Path

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
