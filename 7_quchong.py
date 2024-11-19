repeat_label_str = []

import os
import sys
import cv2
from collections import defaultdict

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


# 视频路径和标签文件夹
group_name = 's10_3_1101_1725' # 视频组名
video_name = 'L2'              # 视频名
worktype = 'labels' # filled_labels, labels

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
box_color = (255, 0, 0)  # 边界框颜色 (B, G, R)，(0, 0, 255)为红色
box_thickness = 2        # 边界框粗细
text_thickness = 2       # 标注文字粗细
text_scale = 0.5         # 标注文字大小（缩放因子）

def quchong_once(label_path, frame_id, other_id):
    with open(label_path, "r") as f:
        lines = f.readlines()
    
    # 解析每一行，将其转换为列表 [class_id, x_center, y_center, width, height, confidence, class_id]
    data = [list(map(float, line.split())) for line in lines]
    for line in data:
        line[-1] = int(line[-1])
        line[0] = int(line[0])
    
    # 用字典统计最后一列重复的行
    last_col_dict = {}
    for i, row in enumerate(data):
        last_col_value = row[-1]
        if last_col_value in last_col_dict:
            last_col_dict[last_col_value].append(i)
        else:
            last_col_dict[last_col_value] = [i]
            
    # 筛选出最后一列重复的行
    duplicates = {k: v for k, v in last_col_dict.items() if len(v) > 1}
    
    if len(duplicates) == 0:
        return
    
    print(label_path)
    
    # 展示图像，假设只存在一项重复
    # 设置到第n帧
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_id)

    ret, frame = cap.read()
    if not ret:
        exit()
        
    label_path = f"{label_folder}/{video_name}_{frame_id}.txt"

    # 画框
    # 在当前帧上绘制边界框和跟踪 ID
    draw_yolo_bbox_with_id(frame, label_path, box_color=box_color, box_thickness=box_thickness, text_thickness=text_thickness, text_scale=text_scale)
    
    # 如果存在重复行，则根据键盘输入选择第二列的较大/较小值
    for key, indices in duplicates.items():
        # 提取第二列较小和较大的值
        rows = [data[idx] for idx in indices]
        left_row = min(rows, key=lambda x: x[1])  # 根据第二列 (x_center) 找较小的行
        right_row = max(rows, key=lambda x: x[1])  # 根据第二列 (x_center) 找较大的行
        up_row = min(rows, key=lambda x: x[2]) # 根据第三列 (y_center) 找较小的行
        down_row = max(rows, key=lambda x: x[2]) # 根据第三列 (y_center) 找较大的行
        
        print(f"重复的 class_id {key} 对应的行：")
        # for row in rows:
        #     print(row)
        
        # 显示图片
        cv2.imshow(f"Frame {frame_id}", frame)
        tap = cv2.waitKey(0) & 0xff
        if tap == ord('q'):
            exit(1)
        
        # 等待用户输入
        while True:
            if tap == ord('a'):
                selected_row = left_row
                # 修改所选行的最后一列为 142
                selected_row[-1] = other_id
                print("选择了较小的行")
                
                # 删除较大的框
                # data.remove(left_row)
                # print("删除了较左的行")
                break
            elif tap == ord('d'):
                selected_row = right_row
                # 修改所选行的最后一列为 142
                selected_row[-1] = other_id
                print("选择了较大的行")
                
                # 删除较大的框
                # data.remove(right_row)
                # print("删除了较右的行")
                break
            elif tap == ord('s'):
                # 删除较大的框
                data.remove(down_row)
                print("删除了较下的行")
                break
            elif tap == ord('w'):
                # 删除较大的框
                data.remove(up_row)
                print("删除了较上的行")
                break
            else:
                tap = input("请输入 a 或 d")
                continue
        
    # 保存修改后的文件
    with open(label_path, 'w') as file:
        for row in data:
            file.write(" ".join(map(str, row)) + "\n")

    print("文件已更新")
    

def quchong_main():
    # repeat_label_list = repeat_label_str.splitlines()
    repeat_label_list = inconsistent_files
    sorted_paths = sorted(repeat_label_list, key=lambda x: int(x.split('_')[-1].split('.')[0]))
    
    processed = 0
    total = len(sorted_paths)
    for label_file in sorted_paths:
        frame_id = int(label_file.split('_')[-1].split('.')[0])
        other_id = int(sys.argv[1])
        quchong_once(label_file, frame_id, other_id)
        processed += 1
        print(f"已经处理 {processed} / {total}")

directory_path = f"./{group_name}/{video_name}"
# 执行分析
total_files, total_lines, total_ids, id_count, inconsistent_files, invalid_lines_count, line_count_per_file, frames_with_target_object_count = analyze_annotation_files(directory_path+"/"+worktype)

quchong_main()