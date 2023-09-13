#!/bin/bash

# 脚本描述: This script is used to package FactoryTest and copy files to the target folder based on command line arguments.

# 定义 Usage 函数
usage() {
    echo "Usage: packaging.sh [-F/--onefile] [-D/--onedir]"
    echo "If no arguments are provided, default packaging option will be used."
    echo "Options: -F/--onefile = package as a single executable file"
    echo "         -D/--onedir  = package as a directory containing executables"
    exit 1
}

# 定义 spec_file 变量
spec_file="FactoryTest-onefile.spec"
DIST_NAME="QYTechFactoryTest"
VERSION="V1.0.0"

# 获取当前日期，格式为 YYYYMMDD
datetime=$(date +"%Y%m%d-%H%M")

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case "$1" in
    -F | --onefile)
        spec_file="FactoryTest-onefile.spec"
        ;;
    -D | --onedir)
        spec_file="FactoryTest-onedir.spec"
        ;;
    *)
        usage
        ;;
    esac
    shift
done

# 检查 .venv 环境是否存在，如果不存在则创建
if [ ! -d .venv_unix ]; then
    echo "Creating a new virtual environment..."
    python3 -m venv .venv_unix
fi

# 激活虚拟环境
echo "Activating the virtual environment..."
source .venv_unix/bin/activate

# 确保安装了 PyInstaller
echo "Installing PyInstaller..."
pip install pyinstaller

# 从 requirements.txt 中安装所需的包
echo "Installing required packages from requirements.txt..."
pip install -r requirements.txt

# 使用指定的 spec 文件构建可执行文件
echo "Building the executable using $spec_file..."
pyinstaller --clean --noconfirm "$spec_file"

# 创建目标文件夹的名称，格式为 FactoryTest-YYYYMMDD
target_folder="release/FactoryTest-$VERSION-$datetime"

# 检查目标文件夹是否存在，如果存在则删除
if [ -d "$target_folder" ]; then
    echo "Deleting existing target folder: $target_folder..."
    rm -rf "$target_folder"
fi

# 创建新的目标文件夹
echo "Creating target folder: $target_folder"
mkdir -p "$target_folder"

# 检查 spec_file 的值并进行相应的文件拷贝操作
echo "Copying configuration folder (config) to $target_folder..."
cp -r config "$target_folder"

echo "Copying factory test binary folder (factorytest_bin) to $target_folder..."
cp -r factorytest_bin "$target_folder"

# 复制文档
cp "docs/README.pdf" "$target_folder"

if [ "$spec_file" == "FactoryTest-onefile.spec" ]; then
    echo "Copying executable file in single-file mode (dist/$DIST_NAME) to $target_folder..."
    cp "dist/$DIST_NAME" "$target_folder"
elif [ "$spec_file" == "FactoryTest-onedir.spec" ]; then
    echo "Copying executable file in directory mode (dist/$DIST_NAME) to $target_folder/$DIST_NAME..."
    cp -r "dist/$DIST_NAME/"* "$target_folder"
fi

# 将打包后的文件用7z压缩并删除中间文件夹
7z a -r "$target_folder.7z" "./$target_folder/*"

if [ -d "$target_folder" ]; then
    echo "Deleting existing target folder: $target_folder..."
    rm -rf "$target_folder"
fi

# 停用虚拟环境
echo "Deactivating the virtual environment..."
deactivate

echo "Packaging completed."
