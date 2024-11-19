group_name='s10_3_1101_1725'

IFS='_' read -r ROOT_GROUP_NAME _ <<< "$group_name"
echo $ROOT_GROUP_NAME

# scp -r -P 1938 ./$group_name/fine_labels nao@npu.seekecho.cn:/home/nao/mxy/biaozhu_20241020/fine_labels/$group_name

# ssh -p 1938 nao@npu.seekecho.cn "sshpass -p 'data_pass' scp -r -P 10126 /home/nao/mxy/biaozhu_20241020/fine_labels/$group_name data_pass@10.68.44.250:/data/F/data_pass/fine_labels/"

# ssh -p 1938 nao@npu.seekecho.cn "rm -r /home/nao/mxy/biaozhu_20241020/fine_labels/$group_name"
# rsync --partial --progress -e "ssh -p 1938" --human-readable -r ./$group_name/fine_labels/ nao@npu.seekecho.cn:/home/nao/mxy/biaozhu_20241020/fine_labels/$group_name

sshpass -p 'data_pass' ssh -p 10126 data_pass@10.68.44.250 "rm -r /data/F/data_pass/fine_labels/$ROOT_GROUP_NAME/$group_name"
sshpass -p 'data_pass' rsync --partial --progress -e "ssh -p 10126" --human-readable --exclude=".DS_Store" -r ./$group_name/fine_labels/ data_pass@10.68.44.250:/data/F/data_pass/fine_labels/$ROOT_GROUP_NAME/$group_name
sshpass -p 'data_pass' ssh -p 10126 data_pass@10.68.44.250 "find /data/F/data_pass/fine_labels/$ROOT_GROUP_NAME/$group_name -type d -mindepth 1 -maxdepth 1 | sort"