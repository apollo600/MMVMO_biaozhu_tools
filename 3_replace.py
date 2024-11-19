import os
import re
import sys

def replace_text_in_file(file_path, target, replacement):
    
    # 使用正则表达式来匹配独立的数字或文本
    target_pattern = r'\b' + re.escape(target) + r'\b'
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        
    # 计算替换前的匹配项数量
    matches = re.findall(target_pattern, content)
    count = len(matches)
    
    if count > 0:
        # 执行替换
        content = re.sub(target_pattern, replacement, content)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
    
    return count

def replace_text_in_all_txt_files(directory, target, replacement):
    modified_files_count = 0
    total_replacements = 0
    for root, _, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith('.txt'):
                file_path = os.path.join(root, file_name)
                replacements = replace_text_in_file(file_path, target, replacement)
                if replacements > 0:
                    modified_files_count += 1
                    total_replacements += replacements
    return modified_files_count, total_replacements

if __name__ == "__main__":
    
    # 手动定义要处理的视频组、视频
    group_name = 's10_3_1101_1725' # 视频组名
    video_name = 'L2'              # 视频名
    
    # 手动定义需要替换的字段 A 和 B
    target_id = int(sys.argv[1])
    replacement_id = int(sys.argv[2])
    target_text = f" {target_id}"  # 替换为你想要替换的字段
    replacement_text = f" {replacement_id}"  # 替换为你想替换成的字段

    # 目标目录
    directory_path = f"./{group_name}/{video_name}" 

    # 执行替换
    modified_files, total_replacements = replace_text_in_all_txt_files(directory_path+'/labels', target_text, replacement_text)
    print(f"已将目录 {directory_path} 下所有 txt 文件中的 '{target_text}' 替换为 '{replacement_text}'。")
    print(f"共修改了 {modified_files} 个文件，执行了 {total_replacements} 次替换。")