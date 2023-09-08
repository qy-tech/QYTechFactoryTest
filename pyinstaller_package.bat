@ECHO OFF

REM 定义SPEC_FILE变量
SET SPEC_FILE=FactoryTest-onefile.spec

REM 解析命令行参数
:parse_args
IF "%~1"=="" GOTO pyinstaller_packaging
IF "%~1"=="-F" GOTO onefile
IF "%~1"=="--onefile" GOTO onefile
IF "%~1"=="-D" GOTO onedir
IF "%~1"=="--onedir" GOTO onedir
GOTO usage

:pyinstaller_packaging
REM 检查.venv环境是否存在，如果不存在则创建
IF NOT EXIST .venv (
    ECHO Creating a new virtual environment...
    python -m venv .venv
)

REM 激活虚拟环境
ECHO Activating the virtual environment...
call .venv\Scripts\activate

REM 确保安装了pyinstaller
ECHO Installing PyInstaller...
pip install pyinstaller

REM 从requirements.txt中安装所需的包
ECHO Installing required packages from requirements.txt...
pip install -r requirements.txt

REM 使用指定的spec文件构建可执行文件
ECHO Building the executable using %SPEC_FILE%...
pyinstaller --clean --noconfirm "%SPEC_FILE%"

REM 停用虚拟环境
ECHO Deactivating the virtual environment...
deactivate
EXIT /B 0

:onefile
SET SPEC_FILE=FactoryTest-onefile.spec
shift
GOTO pyinstaller_packaging

:onedir
SET SPEC_FILE=FactoryTest-onedir.spec
shift
GOTO pyinstaller_packaging

@REM 定义Usage函数
:usage
ECHO USAGE: packaging.bat [-F/--onefile] [-D/--onedir]
ECHO No ARGS means use the default packing option
ECHO WHERE: -F/--onefile = packing one exe file
ECHO        -D/--onedir  = packing one dir containing exe
EXIT /B 1