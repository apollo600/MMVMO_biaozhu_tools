import os

group_name = 's10_3_1101_1725' # 视频组名
fine_label_dir = f'{group_name}/fine_labels'

if os.path.exists(fine_label_dir):
    os.system(f'rm -r {fine_label_dir}')

os.system(f'mkdir -p {fine_label_dir}')

def pack_once(video):
    os.system(f'mkdir -p {fine_label_dir}/{video}')
    
    root_dir = os.path.join(group_name, video)
    os.system(f'cp -r {root_dir}/labels {fine_label_dir}/{video}')
    os.system(f'cp -r {root_dir}/filled_labels {fine_label_dir}/{video}')
    os.system(f'cp -r {root_dir}/snapshot.png {fine_label_dir}/{video}')

    print(f'打包 {root_dir} 完成')
    

# 获取所有视频名称
videos = []
for item in os.listdir(group_name):
    if item == 'fine_labels':
        continue
    item_path = os.path.join(group_name, item)
    if os.path.isdir(item_path):
        videos.append(item)
videos = sorted(videos)

for video in videos:
    pack_once(video)