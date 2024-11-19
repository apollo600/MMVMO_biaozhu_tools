import os
import numpy as np
import sys

# 手动定义要处理的视频组、视频
group_name = 's10_3_1101_1725' # 视频组名
video_name = 'L2'              # 视频名

# 原始标注文件的路径和补全后的标注文件存储路径
original_annotations_path = f"./{group_name}/{video_name}"
filled_labels_path = original_annotations_path + "/filled_labels"

if not os.path.exists(filled_labels_path):
    os.makedirs(filled_labels_path)

def read_annotation_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    annotations = []
    for line in lines:
        items = line.strip().split()
        category = int(items[0])
        center_x = float(items[1])
        center_y = float(items[2])
        width = float(items[3])
        height = float(items[4])
        confidence = float(items[5])
        object_id = int(items[6])
        annotations.append((category, center_x, center_y, width, height, confidence, object_id))
    return annotations

def write_annotation_file(file_path, annotations):
    with open(file_path, 'w') as f:
        for ann in annotations:
            f.write(f"{ann[0]} {ann[1]:.6f} {ann[2]:.6f} {ann[3]:.6f} {ann[4]:.6f} {ann[5]:.6f} {ann[6]}\n")

def interpolate_annotations(prev_ann, next_ann, alpha):
    return [
        prev_ann[0],  # 类别编号保持一致
        prev_ann[1] * (1 - alpha) + next_ann[1] * alpha,  # 中心X坐标插值
        prev_ann[2] * (1 - alpha) + next_ann[2] * alpha,  # 中心Y坐标插值
        prev_ann[3] * (1 - alpha) + next_ann[3] * alpha,  # X宽度插值
        prev_ann[4] * (1 - alpha) + next_ann[4] * alpha,  # Y高度插值
        prev_ann[5] * (1 - alpha) + next_ann[5] * alpha,  # 信息度插值
        prev_ann[6]  # ID编号保持一致
    ]

def is_within_bounds(annotation):
    center_x, center_y, width, height = annotation[1], annotation[2], annotation[3], annotation[4]
    # 检查插值后的标注是否超出视频范围（假设视频范围为 [0, 1]）
    if (0.005 < center_x - width / 2 < 0.995 and 0.005 < center_x + width / 2 < 0.995 and
            0.005 < center_y - height / 2 < 0.995 and 0.005 < center_y + height / 2 < 0.995):
        return True
    return False

def is_at_border(annotation):
    center_x, center_y, width, height = annotation[1], annotation[2], annotation[3], annotation[4]
    # 检查目标是否在视频边界位置（假设边界位置为 [0, 0.05] 或 [0.95, 1]）
    if (center_x - width / 2 <= 0.025 or center_x + width / 2 >= 0.975 or
            center_y - height / 2 <= 0.025 or center_y + height / 2 >= 0.975):
        return True
    return False

def fill_missing_annotations(ignore_ids, max_missing_frames, specific_frame_ranges):
    # 读取所有标注文件，按帧序号排序
    annotation_files = sorted([f for f in os.listdir(original_annotations_path + "/labels") if f.endswith('.txt')],
                              key=lambda x: int(x.split('_')[-1].split('.')[0]))
    
    # 创建一个字典，存储每一帧中每个目标的标注
    annotations_by_frame = {}
    for file_name in annotation_files:
        frame_number = int(file_name.split('_')[-1].split('.')[0])
        annotations_by_frame[frame_number] = read_annotation_file(os.path.join(original_annotations_path + "/labels", file_name))
    
    # 获取所有帧的编号
    all_frames = sorted(annotations_by_frame.keys())
    
    # 创建一个字典，存储每个目标在所有帧中的标注
    object_tracks = {}
    for frame_number in all_frames:
        for ann in annotations_by_frame[frame_number]:
            object_id = ann[6]
            if object_id not in object_tracks:
                object_tracks[object_id] = {}
            object_tracks[object_id][frame_number] = ann
    
    # 对每个目标进行插值补全
    for object_id, track in object_tracks.items():
        frames_with_ann = sorted(track.keys())
        
        # 遍历有标注的帧，查找缺失的部分并进行插值
        for i in range(len(frames_with_ann) - 1):
            start_frame = frames_with_ann[i]
            end_frame = frames_with_ann[i + 1]

            # 如果缺失段的前一帧和后一帧中目标在视频边界位置，则不进行补全
            if is_at_border(track[start_frame]) or is_at_border(track[end_frame]):
                continue
            
            # 如果缺失段超过最大允许帧数，则不进行补全
            if (end_frame - start_frame - 1) > max_missing_frames:
                continue

            # 如果在特定帧范围内且该ID在忽略列表中，不进行补全
            if any(start <= start_frame <= end or start <= end_frame <= end for start, end in specific_frame_ranges) and object_id in ignore_ids:
                continue
            
            # 如果两个有标注的帧之间存在缺失帧，则进行插值
            if end_frame > start_frame + 1:
                num_missing_frames = end_frame - start_frame - 1
                for j in range(1, num_missing_frames + 1):
                    alpha = j / (num_missing_frames + 1)
                    interpolated_ann = interpolate_annotations(track[start_frame], track[end_frame], alpha)
                    if is_within_bounds(interpolated_ann):
                        if (start_frame + j) not in annotations_by_frame:
                            annotations_by_frame[start_frame + j] = []
                        annotations_by_frame[start_frame + j].append(interpolated_ann)
    
    # 将补全后的标注写入新的文件中
    for frame_number, annotations in annotations_by_frame.items():
        original_annotations = read_annotation_file(os.path.join(original_annotations_path + "/labels", f"{video_name}_{frame_number}.txt"))
        # 合并原始标注和插值标注，确保原始标注不被修改或丢弃
        merged_annotations = original_annotations + [ann for ann in annotations if ann not in original_annotations]
        filled_file_path = os.path.join(filled_labels_path, f"{video_name}_{frame_number}.txt")
        write_annotation_file(filled_file_path, merged_annotations)

if __name__ == "__main__":

    # 用户可输入要忽略的ID列表，最大允许缺失帧数，和特定帧范围
    
    # 忽略特定帧范围内对特定ID的插值
    # ignore_ids = [13]  
    # specific_frame_ranges = [(200, )] # 可指定多段，逗号隔开即可 # 视频均为每秒30帧，可以自行换算
    ignore_ids = [6]  
    specific_frame_ranges = [(540, 600)] # 可指定多段，逗号隔开即可 # 视频均为每秒30帧，可以自行换算

    # 最大允许缺失帧数
    max_missing_frames = int(sys.argv[1])  # 缺失8秒则不插值，可以自行调整
    
    
    fill_missing_annotations(ignore_ids, max_missing_frames, specific_frame_ranges)
