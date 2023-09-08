# 定义Usage函数
function usage {
    Write-Host "USAGE: packaging.bat [-F/--onefile] [-D/--onedir]"
    Write-Host "No ARGS means use default packing option"
    Write-Host "WHERE: -F/--onefile = packing one exe file"
    Write-Host "       -D/--onedir  = packing one dir contain exe"
    exit 1
}

# 定义SPEC_FILE变量
$SPEC_FILE="FactoryTest-onefile.spec"

# 解析命令行参数
foreach ($arg in $args) {
    switch ($arg) {
        "-F" { $SPEC_FILE="FactoryTest-onefile.spec" }
        "--onefile" { $SPEC_FILE="FactoryTest-onefile.spec" }
        "-D" { $SPEC_FILE="FactoryTest-onedir.spec" }
        "--onedir" { $SPEC_FILE="FactoryTest-onedir.spec" }
        default { usage }
    }
}

# 检查.venv环境是否存在，如果不存在则创建
if (-not (Test-Path .venv)) {
    Write-Host "Creating a new virtual environment..."
    python -m venv .venv
}

# 激活虚拟环境
Write-Host "Activating the virtual environment..."
.venv\Scripts\activate

# 确保安装了pyinstaller
Write-Host "Installing PyInstaller..."
pip install pyinstaller

# 从requirements.txt中安装所需的包
Write-Host "Installing required packages from requirements.txt..."
pip install -r requirements.txt

# 使用指定的spec文件构建可执行文件
Write-Host "Building the executable using $SPEC_FILE..."
pyinstaller --clean --noconfirm "$SPEC_FILE"

# 停用虚拟环境
Write-Host "Deactivating the virtual environment..."
deactivate
