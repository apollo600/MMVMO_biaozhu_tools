import os
import sys
import cv2

output = "tmp.txt"
id = int(sys.argv[1])
if len(sys.argv) >= 3:
    frame_start = int(sys.argv[2])
else:
    frame_start = -1

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
box_color = (0, 0, 255)  # 边界框颜色 (B, G, R)，(0, 0, 255)为红色
box_thickness = 2        # 边界框粗细
text_thickness = 2       # 标注文字粗细
text_scale = 1.0         # 标注文字大小（缩放因子）

os.system(f"python 4_find.py {id} > {output}")
with open(output, "r") as f:
    lines = f.readlines()
    for line in lines[:3]:
        print(line)
    labels = lines[3:]
sorted_labels = sorted(labels, key=lambda x: int(x.split('_')[-1].split('.')[0]))

for label in sorted_labels:
    frame_id = int(label.split('_')[-1].split('.')[0])
    if frame_start > 0 and frame_id < frame_start:
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
        break
    if key == ord('a'):
        print(label_path)
