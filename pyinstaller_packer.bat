@echo off
:: 脚本描述: 用于打包 FactoryTest 并根据命令行参数将文件复制到目标文件夹。



:: 定义 spec_file 变量
set "spec_file=FactoryTest-onefile.spec"
set "DIST_NAME=QYTechFactoryTest"
set "VERSION=V1.0.0"
:: 获取当前日期，格式为 YYYYMMDD
for /f "tokens=1-4 delims= " %%a in ('wmic os get LocalDateTime ^| find "."') do set "datetime=%%a"
set "datetime=%datetime:~0,8%-%datetime:~8,4%"

:: 解析命令行参数
:parse_args
if "%~1"=="" goto pyinstaller_packaging
if "%~1"=="-F" goto onefile
if "%~1"=="--onefile" goto onefile
if "%~1"=="-D" goto onedir
if "%~1"=="--onedir" goto onedir
goto Usage

:pyinstaller_packaging
:: 检查 .venv 环境是否存在，如果不存在则创建
if not exist .venv_win (
    echo Creating a new virtual environment...
    python -m venv .venv_win
)

:: 激活虚拟环境
echo Activating the virtual environment...
call .venv_win\Scripts\activate

:: 确保安装了 PyInstaller
echo Installing PyInstaller...
pip install pyinstaller

:: 从 requirements.txt 中安装所需的包
echo Installing required packages from requirements.txt...
pip install -r requirements.txt

:: 使用指定的 spec 文件构建可执行文件
echo Building the executable using %spec_file%...
pyinstaller --clean --noconfirm "%spec_file%"

:: 创建目标文件夹的名称，格式为 FactoryTest-YYYYMMDD
set "target_folder=release\FactoryTest-%VERSION%-%datetime%"

:: 检查目标文件夹是否存在，如果存在则删除
if exist "%target_folder%" (
    echo Deleting existing target folder: %target_folder%...
    rmdir /s /q "%target_folder%"
)

:: 创建新的目标文件夹
echo Creating target folder: %target_folder%
mkdir "%target_folder%"

:: 检查 spec_file 的值并进行相应的文件拷贝操作
echo Copying configuration folder (config) to %target_folder%...
xcopy /s /e /i /y "config" "%target_folder%\config"

echo Copying factory test binary folder (factorytest_bin) to %target_folder%...
xcopy /s /e /i /y "factorytest_bin" "%target_folder%\factorytest_bin"

if "%spec_file%"=="FactoryTest-onefile.spec" (
    echo Copying executable file in single-file mode 
    copy "dist\%DIST_NAME%.exe" "%target_folder%" /y
) else if "%spec_file%"=="FactoryTest-onedir.spec" (
    echo Copying executable file in directory mode 
    xcopy /s /e /i /y "dist\%DIST_NAME%" "%target_folder%"
)

:: 停用虚拟环境
@REM echo Deactivating the virtual environment...
@REM deactivate

echo Packaging completed.
exit /b 0

:: 根据命令行参数选择 spec_file
:onefile
set "spec_file=FactoryTest-onefile.spec"
shift
goto pyinstaller_packaging

:onedir
set "spec_file=FactoryTest-onedir.spec"
shift
goto pyinstaller_packaging

:: 定义 Usage 函数
:Usage
echo Usage: packaging.bat [-F/--onefile] [-D/--onedir]
echo If no arguments are provided, default packaging option will be used.
echo Options: -F/--onefile = package as a single executable file
echo          -D/--onedir  = package as a directory containing executables
exit /b 1