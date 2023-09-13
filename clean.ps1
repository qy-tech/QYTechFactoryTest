# 删除指定目录及其内容
# 使用 -Recurse 参数递归删除目录内的所有文件和子目录
# 使用 -Force 参数强制执行删除操作，无需确认提示

# 指定要删除的文件夹路径
$folderPath = "build", "dist", "logs", "result", "release"

# 遍历每个文件夹路径，检查是否存在并删除
foreach ($path in $folderPath) {
    if (Test-Path -Path $path -PathType Container) {
        # 文件夹存在，执行删除操作
        Remove-Item -Path $path -Recurse -Force
        Write-Output "Folder $path has been deleted."
    } else {
        # 文件夹不存在，输出信息
        Write-Output "Folder $path does not exist."
    }
}

