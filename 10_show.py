import os
import cv2
from tqdm import tqdm
import sys

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

# 视频路径和标签文件夹
group_name = 's10_3_1101_1725' # 视频组名
video_name = 'L2'              # 视频名
worktype = sys.argv[1] # filled_labels, labels
if worktype not in ["labels", "filled_labels"]:
    print("Usage python 10_show.py <[labels, filled_labels]>")
    exit(1)

video_path = f'./origin/{group_name}/{video_name}.mp4'
label_folder = f'./{group_name}/{video_name}/{worktype}'


# 打开视频文件
cap = cv2.VideoCapture(video_path)

# 获取视频属性
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# 定义输出视频文件
if worktype == "filled_labels":
    output_path = f"./{group_name}/{video_name}_with_new_filled_labels.mp4"
else:
    output_path = f"./{group_name}/{video_name}_with_new_labels.mp4"

fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 使用 'mp4v' 编码器
out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

# 配置标注样式
box_color = (0, 0, 255)  # 边界框颜色 (B, G, R)，(0, 0, 255)为红色
box_thickness = 2        # 边界框粗细
text_thickness = 2       # 标注文字粗细
text_scale = 1.0         # 标注文字大小（缩放因子）

print(f"输出视频 {video_name} {worktype}")

frame_id = 0

err_labels = []

# 使用 tqdm 显示进度条
with tqdm(total=total_frames, desc="Processing Video", unit="frame") as pbar:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 根据视频名称和帧序号加载对应帧的标签
        label_path = f"{label_folder}/{video_name}_{frame_id}.txt"

        # 在当前帧上绘制边界框和跟踪 ID
        try:
            draw_yolo_bbox_with_id(frame, label_path, box_color=box_color, box_thickness=box_thickness, text_thickness=text_thickness, text_scale=text_scale)
        except ValueError as e:
            print(e)
            err_labels.append(label_path)

        # 写入输出视频
        out.write(frame)

        # 更新进度条
        pbar.update(1)

        frame_id += 1

# 释放资源
cap.release()
out.release()

print(f"输出视频保存为: {output_path}")

if len(err_labels) > 0:
    print("以下标签格式错误:")
    for err_label in err_labels:
        print(err_label)
