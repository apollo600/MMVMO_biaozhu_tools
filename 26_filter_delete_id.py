"""
1_analysis.py 和 11_find_and_visual_all.py 的结合体，还增加了自动添加到标注文件的功能
"""
import os
from collections import defaultdict
import cv2
from enum import Enum
import re

class Anno(Enum):
    DELETE_ID = 1
    SKIP_ID = 2
    STOP = 3

def analyze_annotation_files(directory, target_object_count=100):
    total_files = 0
    total_lines = 0
    id_count = defaultdict(int)
    inconsistent_files = []
    invalid_lines_count = 0
    line_count_per_file = defaultdict(int)
    frames_with_target_object_count = []

    for root, _, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith('.txt'):
                file_path = os.path.join(root, file_name)
                total_files += 1
                ids_in_frame = set()
                with open(file_path, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                    line_count = len(lines)
                    line_count_per_file[len(lines)] += 1
                    total_lines += len(lines)
                    if line_count == target_object_count:
                        frames_with_target_object_count.append(file_name)
                    for line in lines:
                        parts = line.strip().split()
                        if len(parts) != 7:
                            invalid_lines_count += 1
                            continue  # 跳过格式不正确的行
                        _, _, _, _, _, _, obj_id = parts
                        if obj_id in ids_in_frame:
                            inconsistent_files.append(file_path)
                        ids_in_frame.add(obj_id)
                        id_count[obj_id] += 1

    total_ids = len(id_count)
    return total_files, total_lines, total_ids, dict(id_count), inconsistent_files, invalid_lines_count, dict(line_count_per_file), frames_with_target_object_count


def draw_yolo_bbox_with_id(frame, label_path, box_color=(0, 255, 0), box_thickness=2, text_thickness=1, text_scale=0.5):
    height, width, _ = frame.shape
    if os.path.exists(label_path):
        with open(label_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                # 读取标签并解析各个参数
                class_id, x_center, y_center, bbox_width, bbox_height, conf, track_id = map(float, line.strip().split())
                
                # 计算边界框的实际像素坐标
                x_center, y_center, bbox_width, bbox_height = x_center * width, y_center * height, bbox_width * width, bbox_height * height
                x1 = int(x_center - bbox_width / 2)
                y1 = int(y_center - bbox_height / 2)
                x2 = int(x_center + bbox_width / 2)
                y2 = int(y_center + bbox_height / 2)
                
                # 绘制边界框
                cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, box_thickness)
                
                # 绘制跟踪 ID
                label = f'ID {int(track_id)}'
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, text_scale, (255,255,255), text_thickness+2)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, text_scale, box_color, text_thickness)


def find_show_and_annotate(id) -> Anno:
    os.system(f"python 4_find.py {id} > {OUTPUT_FILE}")
    with open(OUTPUT_FILE, "r") as f:
        lines = f.readlines()
        # for line in lines[:3]:
        #     print(line)
        labels = lines[3:]
    sorted_labels = sorted(labels, key=lambda x: int(x.split('_')[-1].split('.')[0]))

    for label in sorted_labels:
        frame_id = int(label.split('_')[-1].split('.')[0])
        if FRAME_START > 0 and frame_id < FRAME_START:
            continue
        
        # 设置到第n帧
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_id)

        ret, frame = cap.read()
        if not ret:
            print("未找到此帧")
            exit()
            
        label_path = f"{label_folder}/{video_name}_{frame_id}.txt"

        # 画框
        # 在当前帧上绘制边界框和跟踪 ID
        draw_yolo_bbox_with_id(frame, label_path, box_color=box_color, box_thickness=box_thickness, text_thickness=text_thickness, text_scale=text_scale)

        # 显示图片
        cv2.imshow(f"Frame {frame_id}", frame)
        key = cv2.waitKey(0) & 0xff
        if key == ord('q'):
            return Anno.STOP
        if key == ord('a'):
            # cv2.destroyAllWindows()
            return Anno.SKIP_ID
        if key == ord('d'):
            # cv2.destroyAllWindows()
            return Anno.DELETE_ID

def get_id_from_line(annotation:str) -> int:
    result = None
    if re.match(regex_delay, annotation):
        match = re.search(regex_delay, annotation)
        result = int(match.group(1))
    elif re.match(regex_arrow, annotation):
        match = re.search(regex_arrow, annotation)
        from_id = int(match.group(1))
        result = from_id
    elif re.match(regex_arrow_with_brackets, annotation):
        match = re.search(regex_arrow_with_brackets, annotation)
        from_id = int(match.group(1))
        result = from_id
    elif re.match(regex_delete, annotation):
        match = re.search(regex_delete, annotation)
        result = match.group(1)
    else:
        raise ValueError(f"Unknown expression '{annotation}'")

    return result

# 手动定义要处理的视频组、视频、标签种类
group_name = 's10_3_1101_1725' # 视频组名
video_name = 'L2'              # 
worktype = 'labels' # filled_labels, labels

# 目标目录
directory_path = f"./{group_name}/{video_name}"

video_path = f'./origin/{group_name}/{video_name}.mp4'
label_folder = f'./{group_name}/{video_name}/{worktype}'

# 打开视频文件
cap = cv2.VideoCapture(video_path)

# 获取视频属性
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 使用 'mp4v' 编码器

# 配置标注样式
box_color = (0, 0, 255)  # 边界框颜色 (B, G, R)，(0, 0, 255)为红色
box_thickness = 2        # 边界框粗细
text_thickness = 2       # 标注文字粗细
text_scale = 1.0         # 标注文字大小（缩放因子）

anno_file_name = "标注记录.txt"
anno_file_path = f"./{group_name}/{video_name}/{anno_file_name}"
anno_backup_path = f"./{group_name}/{video_name}/{anno_file_name}.bak"

SKIP_COUNT = 800
OUTPUT_FILE = "tmp.txt"
FRAME_START = -1

regex_delay = r"^\((\d+)\)$"
regex_delete = r"^-(\d+)$"
regex_arrow = r"^(\d+)->(\d+)$"
regex_arrow_with_brackets = r"^(\d+)->(\d+)\((.*)\)$"

# 进行 analysis，找出所有的 id
total_files, total_lines, total_ids, id_count, inconsistent_files, invalid_lines_count, line_count_per_file, frames_with_target_object_count = analyze_annotation_files(directory_path+"/"+worktype)
print(f"目录 {directory_path} 下的标注文件个数(总帧数)为：{total_files}")
print(f"所有标注文件的总行数(总对象数)为：{total_lines}")
print(f"总 ID 数为：{total_ids}")
print("各 ID 对应的对象个数如下：")

# 备份标注记录文件
os.system(f"cp {anno_file_path} {anno_backup_path}")

# 对于个数 >= 800 的直接跳过
# 查找该 id，依次显示图像，输入 'a' 之后处理该 id，输入 'd' 标注删除该 id
obj_id_todo = []
for obj_id in sorted(id_count.keys(), key=int):
    print(f"ID {obj_id}: {id_count[obj_id]} 个对象")
    
    if id_count[obj_id] >= SKIP_COUNT:
        print(f"大于 {SKIP_COUNT}，跳过")
        continue
    
    # 查找该 id
    anno = find_show_and_annotate(obj_id)
    if anno == Anno.SKIP_ID:
        print("之后处理")
        obj_id_todo.append(obj_id)
        continue
    elif anno == Anno.DELETE_ID:
        print("标注删除")
        
        # 获取标注记录文件
        with open(anno_file_path, "r") as f:
            lines = f.readlines()
        
        # 找到插入位置
        # 找到正确的插入位置
        insert_index = None
        for i, line in enumerate(lines):
            # 提取当前行的id
            line_id = get_id_from_line(line)
            
            if int(line_id) > int(obj_id):
                insert_index = i
                break
            elif int(line_id) == int(obj_id):
                if line == f"-{obj_id}\n":
                    insert_index = -1
                    break
                else:
                    print(f"该 ID 有其他标注存在 {obj_id}")
                    exit(1)
        
        if insert_index is None:
            # 如果没有找到比new_id大的id，插入到文件末尾
            insert_index = len(lines)
        
        if insert_index == -1:
            print("已在标注文件中，跳过")
            continue
        
        # 根据需求生成插入行的格式，假设插入行格式为 "-new_id\n"
        new_line = f"-{obj_id}\n"
        
        # 插入新id并保持顺序
        lines.insert(insert_index, new_line)
        
        # 将更新后的内容写回文件
        with open(anno_file_path, 'w') as file:
            file.writelines(lines)
    elif anno == Anno.STOP:
        print("停止标注")
        break

for obj_id in obj_id_todo:
    print(f"手动处理 ID {obj_id}")