import re
import os

# 视频路径和标签文件夹
group_name = 's10_3_1101_1725' # 视频组名
video_name = 'L2'              # 视频名

file_name = "标注记录.txt"
file_path = f"./{group_name}/{video_name}/{file_name}"

with open(file_path, "r") as f:
    lines = f.readlines()
    
# 定义正则表达式
regex_delay = r"^\((\d+)\)$"
regex_delete = r"^-(\d+)$"
regex_arrow = r"^(\d+)->(\d+)$"
regex_arrow_with_brackets = r"^(\d+)->(\d+)\((.*)\)$"
regex_ignore = r"^#(.*)$"
sub_regex_ge = r"^>=(\d+)$"
sub_regex_lt = r"^<(\d+)$"
sub_regex_between = r"^(\d+)-(\d+)$"

# 数据结构
delay_ids = set()
cmd_id = 0
free_id = 1000
delay_id_map = dict()

# 获取最大帧数
max_frame_id = 0
for file in os.listdir(f"./{group_name}/{video_name}/labels"):
    id = int(file.split('.')[0].split('_')[-1])
    max_frame_id = max(id, max_frame_id)

# 遍历标注文件
for annotation in lines:
    annotation = annotation.replace('\n', '').replace(' ', '')
    if re.match(regex_delay, annotation):
        match = re.search(regex_delay, annotation)
        if match:
            id = int(match.group(1))
            delay_ids.add(id)
            delay_id_map[id] = free_id
            free_id += 1
            cmd_id += 1
            print(f"cmd {cmd_id}: delay {id} map to {delay_id_map[id]}")
    elif re.match(regex_arrow, annotation):
        # print(f"{annotation} 是一个 'a->b' 标注")
        match = re.search(regex_arrow, annotation)
        if not match:
            raise AssertionError(f"regex '{regex_arrow_with_brackets}' SEARCH str '{annotation}' failed")
        
        # 确定 id
        from_id = int(match.group(1))
        to_id = int(match.group(2))
        
        if to_id in delay_ids:
            to_id = delay_id_map[to_id]
            
        cmd = f"python 3_replace.py {from_id} {to_id} > /dev/null"
            
        cmd_id += 1
        print(f"cmd {cmd_id}: {cmd}")
        os.system(cmd)
    elif re.match(regex_arrow_with_brackets, annotation):
        # print(f"{annotation} 是一个 'a->b(...)' 标注")
        
        match = re.search(regex_arrow_with_brackets, annotation)
        if not match:
            raise AssertionError(f"regex '{regex_arrow_with_brackets}' SEARCH str '{annotation}' failed")
        
        # 确定 id
        from_id = int(match.group(1))
        to_id = int(match.group(2))
        
        if to_id in delay_ids:
            to_id = delay_id_map[to_id]
        
        # 匹配帧数范围
        frame_range = [0, 0]
        frame_condition = match.group(3)
        if re.match(sub_regex_ge, frame_condition):
            sub_match = re.search(sub_regex_ge, frame_condition)
            if sub_match:
                start_id = int(sub_match.group(1))
                frame_range = [start_id, max_frame_id]
        elif re.match(sub_regex_lt, frame_condition):
            sub_match = re.search(sub_regex_lt, frame_condition)
            if sub_match:
                end_id = int(sub_match.group(1))
                frame_range = [0, end_id - 1]
        elif re.match(sub_regex_between, frame_condition):
            sub_match = re.search(sub_regex_between, frame_condition)
            if sub_match:
                start_id, end_id = int(sub_match.group(1)), int(sub_match.group(2))
                frame_range = [start_id, end_id - 1]
        else:
            raise NotImplementedError(f"没有被定义的帧数范围表达式 {frame_condition}")
        
        
        # 执行命令
        cmd = f"python 13_replace_range.py {from_id} {to_id} {frame_range[0]} {frame_range[1]} > /dev/null"
        
        cmd_id += 1
        print(f"cmd {cmd_id}: {cmd}")
        os.system(cmd)
    elif re.match(regex_delete, annotation):
        # print(f"{annotation} 是一个 '-a' 标注")
        # annotation = annotation.strip()
        # delete_id = int(annotation.replace('-', ''))
        match = re.search(regex_delete, annotation)
        delete_id = match.group(1)
        cmd = f"python 2_delete.py {delete_id} > /dev/null"
            
        cmd_id += 1
        print(f"cmd {cmd_id}: {cmd}")
        os.system(cmd)
    elif re.match(regex_ignore, annotation):
        print(f"ignore {annotation}")
        pass
    else:
        # print(f"{annotation} 不符合指定类型")
        raise ValueError(f"Unknown expression '{annotation}'")
    
# delay_id 映射回原 id
for delay_id in delay_ids:
    from_id = delay_id_map[delay_id]
    to_id = delay_id
    cmd = f"python 3_replace.py {from_id} {to_id} > /dev/null"
    
    cmd_id += 1
    print(f"cmd {cmd_id}: {cmd}")
    os.system(cmd)
