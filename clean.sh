#!/bin/bash

# 指定要删除的文件夹路径
folderPath=("build" "dist" "logs" "result" "release")

# 遍历每个文件夹路径，检查是否存在并删除
for path in "${folderPath[@]}"; do
    if [ -d "$path" ]; then
        # 文件夹存在，执行删除操作
        rm -rf "$path"
        echo "Folder $path has been deleted."
    else
        # 文件夹不存在，输出信息
        echo "Folder $path does not exist."
    fi
done

# 输出完成信息
echo "Deletion process completed."
