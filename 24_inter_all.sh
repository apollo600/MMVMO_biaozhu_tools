#!/bin/bash

# 指定你要查看的文件夹路径
group_name='s10_3_1101_1725' # 视频组名

# 获取所有子文件夹，并存储在数组中
folders=($(find "$group_name" -mindepth 1 -maxdepth 1 -type d | sort))

# # 输出文件夹列表
# echo "文件夹列表："
# for folder in "${folders[@]}"; do
#     echo "$folder"
# done

# 遍历文件夹并进行操作
for folder in "${folders[@]}"; do
    echo "处理文件夹: $folder"
    IFS='/' read -r G V <<< "$folder"
    python 9_change_video.py $G $V
    
    first_char=${V:0:1}
    if [ "$first_char" == "G" ]; then
        python 22_inter_new.py 15
    else
        python 22_inter_new.py 30
    fi

    python 10_show.py filled_labels
done
