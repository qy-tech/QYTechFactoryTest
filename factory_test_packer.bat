@echo off

REM 指定要删除的文件夹路径
set "folder_to_delete=factorytest_bin"

REM 检测文件夹是否存在并删除
if exist "%folder_to_delete%" (
    echo Deleting %folder_to_delete%...
    rmdir /s /q "%folder_to_delete%"
    echo Folder %folder_to_delete% deleted.
) else (
    echo Folder %folder_to_delete% does not exist.
)

echo Pushing factorytest_script to the device...

REM factorytest_script推送到设备
adb push factorytest_script /tmp

echo Executing factory_test_packer.sh on the device...

REM 在设备上执行 factory_test_packer.sh
adb shell "chmod +x /tmp/factorytest_script/factory_test_packer.sh && /tmp/factorytest_script/factory_test_packer.sh"

echo Pulling the generated factorytest_bin folder back to the local machine...

REM 将生成的 factorytest_bin 文件夹pull到本地
adb pull /tmp/factorytest_bin .

echo Cleaning up temporary files on the device...

REM 删除临时文件
adb shell "rm -rf /tmp/factorytest_*"

echo Script execution completed.