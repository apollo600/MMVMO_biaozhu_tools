import os
import sys
import re

# 要遍历的文件夹路径
folder_path = "./"

# 要替换的内容
old_groups = set()
new_group = sys.argv[1]
# old_group_name = f"group_name = '{old_group}'"
# new_group_name = f"group_name = '{new_group}'"
group_pattern = r"(group_name\s*=\s*')([^']*)(')"

if len(sys.argv) < 3:
    print(f"Usage: python {os.path.basename(__file__)} <new_group_name> <new_video_name>")
    exit(1)

old_videos = set()
new_video = sys.argv[2]
# old_video_name = f"video_name = '{sys.argv[1]}'"
# new_video_name = f"video_name = '{sys.argv[2]}'"
video_pattern = r"(video_name\s*=\s*')([^']*)(')"

# 遍历文件夹并找到所有 .py 文件
for root, dirs, files in os.walk(folder_path):
    for file_name in files:
        if file_name.endswith(".py") or file_name.endswith(".sh"):
            try:
                tool_id = int(file_name.split('_')[0])
            except:
                continue
            if tool_id == 9:
                continue
            
            file_path = os.path.join(root, file_name)
            
            # 读取文件内容
            with open(file_path, 'r') as file:
                file_data = file.read()
            
            # 替换内容
            # file_data = file_data.replace(old_group_name, new_group_name)
            match = re.search(group_pattern, file_data)
            if match:
                old_groups.add(match.group(2))
            file_data = re.sub(group_pattern, r"\1" + new_group + r"\3", file_data)
            
            if tool_id != 14 and tool_id != 15 and tool_id != 20:
                match = re.search(video_pattern, file_data)
                if match:
                    old_videos.add(match.group(2))
                file_data = re.sub(video_pattern, r"\1" + new_video + r"\3", file_data)
                # file_data = file_data.replace(old_video_name, new_video_name)
            
            # 将修改后的内容写回文件
            with open(file_path, 'w') as file:
                file.write(file_data)

print(f"替换完成！\n{old_groups} -> {new_group}\n{old_videos} -> {new_video}")