# 脚本描述: 用于打包 FactoryTest 并根据命令行参数将文件复制到目标文件夹。

# 定义 Usage 函数
function Usage {
    Write-Host "Usage: packaging.ps1 [-F/--onefile] [-D/--onedir]"
    Write-Host "If no arguments are provided, default packaging option will be used."
    Write-Host "Options: -F/--onefile = package as a single executable file"
    Write-Host "         -D/--onedir  = package as a directory containing executables"
    exit 1
}

# 定义 spec_file 变量
$spec_file = "FactoryTest-onefile.spec"
$DIST_NAME = "QYTechFactoryTest"
$VERSION="V1.0.0"
# 获取当前日期，格式为 YYYYMMDD
$datetime = Get-Date -Format "yyyyMMdd-HHmm"

# 解析命令行参数
foreach ($arg in $args) {
    switch ($arg) {
        "-F" { $spec_file="FactoryTest-onefile.spec" }
        "--onefile" { $spec_file="FactoryTest-onefile.spec" }
        "-D" { $spec_file="FactoryTest-onedir.spec" }
        "--onedir" { $spec_file="FactoryTest-onedir.spec" }
        default { usage }
    }
}

# 检查 .venv 环境是否存在，如果不存在则创建
if (-Not (Test-Path .venv_win)) {
    Write-Host "Creating a new virtual environment..."
    python -m venv .venv_win
}

# 激活虚拟环境
Write-Host "Activating the virtual environment..."
.venv_win/Scripts/Activate

# 确保安装了 PyInstaller
Write-Host "Installing PyInstaller..."
pip install pyinstaller

# 从 requirements.txt 中安装所需的包
Write-Host "Installing required packages from requirements.txt..."
pip install -r requirements.txt

# 使用指定的 spec 文件构建可执行文件
Write-Host "Building the executable using $spec_file..."
pyinstaller --clean --noconfirm "$spec_file"

# 创建目标文件夹的名称，格式为 FactoryTest-YYYYMMDD
$target_folder = "release/FactoryTest-$VERSION-$datetime"

# 检查目标文件夹是否存在，如果存在则删除
if (Test-Path $target_folder -PathType Container) {
    Write-Host "Deleting existing target folder: $target_folder..."
    Remove-Item $target_folder -Recurse -Force
}

# 创建新的目标文件夹
Write-Host "Creating target folder: $target_folder"
New-Item -Path $target_folder -ItemType Directory | Out-Null

# 检查 spec_file 的值并进行相应的文件拷贝操作
Write-Host "Copying configuration folder (config) to $target_folder..."
Copy-Item -Path "config" -Destination $target_folder -Recurse

Write-Host "Copying factory test binary folder (factorytest_bin) to $target_folder..."
Copy-Item -Path "factorytest_bin" -Destination $target_folder -Recurse

# 复制文档
Copy-Item -Path "docs/README.pdf" -Destination $target_folder
Copy-Item -Path "docs/changelog.pdf" -Destination $target_folder

if ($spec_file -eq "FactoryTest-onefile.spec") {
    Write-Host "Copying executable file in single-file mode (dist/$DIST_NAME) to $target_folder..."
    Copy-Item -Path "dist/$DIST_NAME.exe" -Destination $target_folder
}
elseif ($spec_file -eq "FactoryTest-onedir.spec") {
    Write-Host "Copying executable file in directory mode (dist/$DIST_NAME) to $target_folder/$DIST_NAME..."
    Copy-Item -Path "dist\$DIST_NAME\*" -Destination $target_folder -Recurse -Force
}

# 将打包后的文件用7z压缩并删除中间文件夹
7z a -r "$target_folder.7z" "./$target_folder/*"

if (Test-Path $target_folder -PathType Container) {
    Write-Host "Deleting existing target folder: $target_folder..."
    Remove-Item $target_folder -Recurse -Force
}

# 停用虚拟环境
Write-Host "Deactivating the virtual environment..."
deactivate

Write-Host "Packaging completed."