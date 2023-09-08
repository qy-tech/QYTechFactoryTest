#!/bin/bash

# 定义Usage函数
usage() {
    echo "USAGE: packaging.bat [-F/--onefile] [-D/--onedir]"
    echo "No ARGS means use default packing option"
    echo "WHERE: -F/--onefile = packing one exe file"
    echo "       -D/--onedir  = packing one dir contain exe"
    exit 1
}

# 定义SPEC_FILE变量
SPEC_FILE="FactoryTest-onefile.spec"

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case "$1" in
    -F | --onefile)
        SPEC_FILE="FactoryTest-onefile.spec"
        ;;
    -D | --onedir)
        SPEC_FILE="FactoryTest-onedir.spec"
        ;;
    *)
        usage
        ;;
    esac
done

# 检查.venv环境是否存在，如果不存在则创建
if [ ! -d .venv ]; then
    echo "Creating a new virtual environment..."
    python3 -m venv .venv
fi

# 激活虚拟环境
echo "Activating the virtual environment..."
source .venv/bin/activate

# 确保安装了pyinstaller
echo "Installing PyInstaller..."
pip install pyinstaller

# 从requirements.txt中安装所需的包
echo "Installing required packages from requirements.txt..."
pip install -r requirements.txt

# 使用指定的spec文件构建可执行文件
echo "Building the executable using $SPEC_FILE..."
pyinstaller --clean --noconfirm "$SPEC_FILE"

# 停用虚拟环境
echo "Deactivating the virtual environment..."
deactivate
