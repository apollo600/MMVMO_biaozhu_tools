import os
import sys

group_name = 's10_3_1101_1725' # 视频组名
video_name = 'L2'
backup_name = sys.argv[1] if len(sys.argv) >= 2 else "labels_inter_test"

def pack_once(video):
    fine_label_dir = f'{group_name}/{video}/labels_inter_test'
    if os.path.exists(fine_label_dir):
        os.system(f'rm -r {fine_label_dir}')
    
    root_dir = os.path.join(group_name, video)
    os.system(f'cp -r {root_dir}/labels {fine_label_dir}')

    print(f'备份 {root_dir} 完成')

pack_once(video_name)