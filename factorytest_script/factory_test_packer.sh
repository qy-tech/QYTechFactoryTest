#!/bin/bash

# 作者：Jax
# 创建时间：2023-09-11
# 当前版本：V1.0

# 描述：批量编译并移动Shell脚本文件并删除生成的后缀

# 参数说明：
#   无需提供任何参数。


# 指定源目录和输出目录
source_directory="/tmp/factorytest_script"
output_directory="/tmp/factorytest_bin"

# 创建输出目录（如果不存在）
if [ ! -d "$output_directory" ]; then
    mkdir -p "$output_directory"
fi

# 遍历源目录下的.sh文件
for file in "$source_directory"/*.sh; do
    if [ -f "$file" ]; then
        # 提取文件名
        filename=$(basename "$file" .sh)
        # echo "file $file filename $filename"
        # 使用shc编译成可执行文件
        shc -f "$file"
        
        if [ -f "$file.x" ]; then
            # 移动生成的可执行文件到输出目录并删除生成的后缀
            mv "$file.x" "$output_directory/$filename"
            echo "Generated and moved: $filename"
        else
            echo "Failed to generate: $filename"
        fi
    fi
done

echo "Compilation and moving completed."
