import os
from collections import defaultdict

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

if __name__ == "__main__":
    
    # 手动定义要处理的视频组、视频、标签种类
    group_name = 's10_3_1101_1725' # 视频组名
    video_name = 'L2'              # 
    worktype = 'labels' # filled_labels, labels
    
    # 目标目录
    directory_path = f"./{group_name}/{video_name}"

    # # 目标对象数
    # target_object_count = 200 

    # 执行分析
    total_files, total_lines, total_ids, id_count, inconsistent_files, invalid_lines_count, line_count_per_file, frames_with_target_object_count = analyze_annotation_files(directory_path+"/"+worktype)
    print(f"目录 {directory_path} 下的标注文件个数(总帧数)为：{total_files}")
    print(f"所有标注文件的总行数(总对象数)为：{total_lines}")
    print(f"总 ID 数为：{total_ids}")
    print("各 ID 对应的对象个数如下：")
    for obj_id in sorted(id_count.keys(), key=int):
        print(f"ID {obj_id}: {id_count[obj_id]} 个对象")

    print("各帧包含的对象数统计如下：")
    for line_count, file_count in sorted(line_count_per_file.items()):
        print(f"包含 {line_count} 个对象的帧数：{file_count} 个")

    if inconsistent_files:
        print("以下文件中存在同一帧中重复的 ID，数据不合理：")
        for file_path in inconsistent_files:
            print(file_path)
    else:
        print("所有文件的数据均合理，没有发现同一帧中重复的 ID。")
    print(f"格式不正确的行的个数为：{invalid_lines_count}")
    
    # 将包含 target_object_count 个对象的帧编号保存到 txt 文件中
    # output_file_path = directory_path+"_frames_with_"+str(target_object_count)+"_objects.txt"
    # with open(output_file_path, 'w', encoding='utf-8') as output_file:
    #     for frame in frames_with_target_object_count:
    #         output_file.write(f"{frame}\n")
    # print(f"包含 {target_object_count} 个对象的帧编号已保存到文件：{output_file_path}")