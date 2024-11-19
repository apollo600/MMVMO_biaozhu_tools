import os
import re
import sys

def find_text_in_file(file_path, target):
    target_pattern = r'\b' + re.escape(target) + r'\b'
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # 计算匹配项的数量
    matches = re.findall(target_pattern, content)
    count = len(matches)

    return count

def find_text_in_all_txt_files(directory, target):
    files_with_target_count = 0
    total_target_count = 0
    files_with_target = []
    for root, _, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith('.txt'):
                file_path = os.path.join(root, file_name)
                count = find_text_in_file(file_path, target)
                if count > 0:
                    files_with_target_count += 1
                    total_target_count += count
                    files_with_target.append(file_path)
    return files_with_target_count, total_target_count, files_with_target

if __name__ == "__main__":
    
    # 手动定义要处理的视频组、视频
    group_name = 's10_3_1101_1725' # 视频组名
    video_name = 'L2'              # 视频名
    
    # 手动定义需要查找的字段 A
    find_id = int(sys.argv[1])
    target_text = f" {find_id}"  # 替换为你想要查找的字段

    # 目标目录
    directory_path = f"./{group_name}/{video_name}" 

    # 执行查找
    files_with_target, total_target_count, files_with_target_names = find_text_in_all_txt_files(directory_path+"/labels", target_text)
    print(f"目录 {directory_path}/labels 下包含字段 '{target_text}' 的文件个数为：{files_with_target}")
    print(f"字段 '{target_text}' 的总出现次数为：{total_target_count}")
    print("包含字段的文件名称如下：")
    for file_name in files_with_target_names:
        print(file_name)