@echo off
REM 指定要删除的文件夹路径
set "folderPath=build dist logs result release"

REM 使用空格分隔文件夹路径并进行遍历
for %%i in (%folderPath%) do (
    REM 检查文件夹是否存在
    if exist "%%i" (
        REM 文件夹存在，执行删除操作
        rmdir /s /q "%%i"
        echo Folder %%i has been deleted.
    ) else (
        REM 文件夹不存在，输出信息
        echo Folder %%i does not exist.
    )
)

