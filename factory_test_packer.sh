#!/bin/bash

# 指定要删除的文件夹路径
folder_to_delete="factorytest_bin"

# 检测文件夹是否存在并删除
if [ -d "$folder_to_delete" ]; then
    echo "Deleting $folder_to_delete..."
    rm -rf "$folder_to_delete"
    echo "Folder $folder_to_delete deleted."
else
    echo "Folder $folder_to_delete does not exist."
fi

echo "Pushing factorytest_script to the device..."

# factorytest_script推送到设备
adb push factorytest_script /tmp

echo "Executing factory_test_packer.sh on the device..."

# 在设备上执行 factory_test_packer.sh
adb shell "chmod +x /tmp/factorytest_script/factory_test_packer.sh && /tmp/factorytest_script/factory_test_packer.sh"

echo "Pulling the generated factorytest_bin folder back to the local machine..."

# 将生成的 factorytest_bin 文件夹pull到本地
adb pull /tmp/factorytest_bin .

echo "Cleaning up temporary files on the device..."

# 删除临时文件
adb shell "rm -rf /tmp/factorytest_*"

echo "Script execution completed."
