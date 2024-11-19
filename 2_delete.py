import os
import re
import sys

def delete_lines_with_text(file_path, target):

    target_pattern = r'\b' + re.escape(target) + r'\b'

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    modified = False
    new_lines = []
    deleted_lines_count = 0
    for line in lines:
        if re.search(target_pattern, line):
            deleted_lines_count += 1
            modified = True
        else:
            new_lines.append(line)
    if modified:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(new_lines)
    return modified, deleted_lines_count

def delete_lines_with_text_in_all_txt_files(directory, target):
    modified_files_count = 0
    total_deleted_lines = 0
    modified_files = []
    for root, _, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith('.txt'):
                file_path = os.path.join(root, file_name)
                modified, deleted_lines_count = delete_lines_with_text(file_path, target)
                if modified:
                    modified_files_count += 1
                    total_deleted_lines += deleted_lines_count
                    modified_files.append(file_path)
    return modified_files_count, total_deleted_lines, modified_files

if __name__ == "__main__":
    
    # 手动定义要处理的视频组、视频
    group_name = 's10_3_1101_1725' # 视频组名
    video_name = 'L2'              # 视频名
    
    # 手动定义需要删除的字段 A
    target_id = int(sys.argv[1])
    target_text = f" {target_id}"  # 替换为你想要删除的字段 81 83 88 93 99

    # 目标目录
    directory_path = f"./{group_name}/{video_name}" 

    # 执行删除
    modified_files_count, total_deleted_lines, modified_files_names = delete_lines_with_text_in_all_txt_files(directory_path+"/labels", target_text)
    print(f"目录 {directory_path} 下修改了包含字段 '{target_text}' 的文件个数为：{modified_files_count}")
    print(f"总共删除了 {total_deleted_lines} 行。")
    print("修改了的文件名称如下：")
    for file_name in modified_files_names:
        print(file_name)