# FactoryTestTools

FactoryTestTools 是一个用于打包 Python 程序为可执行文件的工具集合。

## 文件说明

- `FactoryTest-onefile.spec` 和 `FactoryTest-onedir.spec`: PyInstaller 的配置文件，用于定义如何打包 Python 程序。
- `build`: 存放构建过程中的临时文件和日志。
- `dist`: 存放打包后的可执行文件。
- `logs`: 存放日志文件。
- `config`: 存放配置文件。
- `gui_design`: 存放图形用户界面 (GUI) 的设计文件。
- `output`: 存放程序运行时生成的输出文件。
- `pyinstaller_package.bat`: Windows 平台下使用 PyInstaller 打包 Python 程序的批处理脚本。
- `pyinstaller_package.sh`: Unix/Linux 平台下使用 PyInstaller 打包 Python 程序的 Shell 脚本。
- `pyinstaller_package.ps1`: PowerShell 脚本版本的 PyInstaller 打包脚本。
- `requirements.txt`: 存放项目依赖的 Python 包列表。
- `translations`: 存放多语言翻译文件。
- `src`: 存放源代码文件。

## 使用方法

1. 通过运行 `pyinstaller_package.bat` 或 `pyinstaller_package.sh`（取决于你的操作系统），可以将 Python 程序打包为可执行文件。可以通过修改相应的配置文件来自定义打包选项。

2. 打包后的可执行文件将保存在 `dist` 文件夹中。

## 依赖

- Python 3.x
- PyInstaller
- pyqt6>=6.4.2
- pyyaml>=6.0
- pandas>=2.0.3
- adbutils>=1.2.13
