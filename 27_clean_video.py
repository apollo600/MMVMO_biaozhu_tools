import os
import re

CLEAN_UNTIL_GROUP = 10

root = "."

regex_group_id = r'^s(\d+)_.*$'

def clean_a_group(group_dir):
    cmd = f"rm {group_dir}/*.mp4"
    print(f"cmd: {cmd}")
    os.system(cmd)
    
    cmd = f"rm -r ./origin/{group_dir.split('/')[-1]}"
    print(f"cmd: {cmd}")
    os.system(cmd)
    
    for dir in os.listdir(group_dir):
        if dir == 'fine_labels':
            continue
        dir_path = os.path.join(group_dir, dir)
        if os.path.isdir(dir_path):
            video_path = os.path.join(dir_path, f"{dir}.avi")
            cmd = f"rm {video_path}"
            print(f"cmd: {cmd}")
            os.system(cmd)

for dir in os.listdir(root):
    if os.path.isdir(dir):
        match = re.match(regex_group_id, dir)
        if not match:
            continue
        group_id = int(match.group(1))
        print(dir, group_id)
        if group_id < CLEAN_UNTIL_GROUP:
            clean_a_group(os.path.join(root, dir))