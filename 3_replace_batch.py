import os
import re
import json

def replace_text_in_file(file_path, replacements):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    original_content = content
    total_replacements = 0

    # 使用正则表达式以避免包含关系引发的错误替换，并防止替换后的内容与原始内容冲突
    for target, replacement in sorted(replacements.items(), key=lambda x: len(x[0]), reverse=True):
        if target:
            # 使用唯一的占位符避免冲突，匹配独立的数字（前后可以是空格、行首、行尾、或其他分隔符）
            pattern = r'(?<!\d)' + re.escape(target.strip()) + r'(?!\d)'
            replacement_temp = f"##TEMP_{target.strip()}##"
            content, count = re.subn(pattern, replacement_temp, content)
            total_replacements += count

    # 将临时替换的内容替换为最终目标
    for target, replacement in sorted(replacements.items(), key=lambda x: len(x[0]), reverse=True):
        replacement_temp = f"##TEMP_{target.strip()}##"
        content = content.replace(replacement_temp, replacement.strip())
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        return True, total_replacements
    
    return False, 0

def batch_replace_text_in_all_txt_files(directory, replacements):
    modified_files_count = 0
    total_replacements = 0

    for root, _, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith('.txt'):
                file_path = os.path.join(root, file_name)
                modified, replacements_count = replace_text_in_file(file_path, replacements)
                if modified:
                    modified_files_count += 1
                    total_replacements += replacements_count

    return modified_files_count, total_replacements

if __name__ == "__main__":
    
    # 手动定义要处理的视频组、视频
    group_name = 's10_3_1101_1725' # 视频组名
    video_name = 'L2'              # 视频名
    
    # 手动定义需要替换的字段 A1 -> B1, A2 -> B2, ..., A10 -> B10
    replacements = {
        # " 8": " 1",
        # " 1": " 2",
        # " 11": " 3",
        # " 2": " 4",
        # " 3": " 5",
        # " 4": " 6",
        # " 6": " 7",
        # " 9": " 8",
        # " 5": " 9",
        # # " ": " 10",
        # " 7": " 11",
        # # " ": " 12",
        # " 14": " 13",
        # # " ": " 14",
        # # " 43": " 15",
        # # 可以继续添加至多 20 组对应的修改内容
    }
    regex_repla = r"^(\d+)->(\d+)$"
    with open(f"./{group_name}/{video_name}/repla.txt", "r") as f:
        for line in f.readlines():
            match = re.search(regex_repla, line)
            if match:
                from_id = match.group(1)
                to_id = match.group(2)
                if int(from_id) == int(to_id):
                    continue
                replacements[from_id] = to_id
    print(json.dumps(replacements, indent=4, ensure_ascii=False))

    # 目标目录
    directory_path = f"./{group_name}/{video_name}" 

    # 执行批量替换
    modified_files, total_replacements = batch_replace_text_in_all_txt_files(directory_path+"/labels", replacements)
    print(f"已将目录 {directory_path} 下所有 txt 文件中的指定字段批量替换。")
    print(f"共修改了 {modified_files} 个文件，执行了 {total_replacements} 次替换。")