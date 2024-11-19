# /data/F/wurq/mvmo_origin_videos/runs/track/s2_3_1009_1540/G
# /data/F/data_pass/original_videos/1009new_syn/s2_3_1009_1540

group_name='s10_3_1101_1725'

IFS='_' read -r ROOT_GROUP_NAME _ <<< "$group_name"
echo $ROOT_GROUP_NAME

set -ex

# 机器初标注结果
# ssh -p 1938 nao@npu.seekecho.cn "sshpass -p 'data_pass' scp -r -P 10126 data_pass@10.68.44.250:/data/F/wurq/mvmo_origin_videos/runs/track/$group_name /home/nao/mxy/biaozhu_20241020/"

# 原视频
# ssh -p 1938 nao@npu.seekecho.cn "sshpass -p 'data_pass' scp -r -P 10126 data_pass@10.68.44.250:/data/F/data_pass/original_videos/1009new_syn/$group_name /home/nao/mxy/biaozhu_20241020/origin/"

# 从 BZPT 拷贝到本机
# scp -r -P 1938 nao@npu.seekecho.cn:/home/nao/mxy/biaozhu_20241020/$group_name ./
# scp -r -P 1938 nao@npu.seekecho.cn:/home/nao/mxy/biaozhu_20241020/origin/$group_name ./origin/
# rsync --partial --progress -e "ssh -p 1938" --human-readable -r nao@npu.seekecho.cn:/home/nao/mxy/biaozhu_20241020/s2_3_1009_1540 ./
# rsync --partial --progress -e "ssh -p 1938" --human-readable -r nao@npu.seekecho.cn:/home/nao/mxy/biaozhu_20241020/origin/s2_3_1009_1540 ./origin/

# 从 data_pass 拷贝到本机
sshpass -p 'data_pass' rsync --partial --progress -e "ssh -p 10126" --human-readable -r data_pass@10.68.44.250:/data/F/wurq/mvmo_origin_videos/runs/track/$group_name ./
sshpass -p 'data_pass' rsync --partial --progress -e "ssh -p 10126" --human-readable -r data_pass@10.68.44.250:/data/F/data_pass/original_videos/1009new_syn/$ROOT_GROUP_NAME/$group_name ./origin/