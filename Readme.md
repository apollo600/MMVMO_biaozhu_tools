# 注意事项

## 整体流程

1. 切换至视频组

    ```shell
    python 9_change_video.py <group_name> <video_name>
    ```

2. 拉取视频，预处理（生成视频），备份

    ```shell
    ./17_fetch.sh && python 19_cp.py && ./23_show_all.sh
    ```

3. 对视频的主体目标依次进行跟踪，按照以下格式进行标注
    > 标注文件记录在 group_name/video_name/标注记录.txt 中
   1. `-id`，删除该 id
   2. `id1->id2`，将所有的 id1 替换成 id2
   3. `id1->id2(>=tt | <tt | tt1-tt2)`，在指定时间 `tt` 之后/之前将 id1 替换成 id2（tt 用帧数表示）
      1. `>=tt`，[tt, MAX)
      2. `<tt`，[0, tt)
      3. `tt1-tt2`，[tt1, tt2)
   4. `(id)`，该 id 本身存在重复赋予情况，需要最后再处理该 id（即 `id` 既是src也是dst）
    > 针对 `id1->id2` 类型，检查有没有相同的 `id1` 转化成 `id2`
    > 针对最后处理的类型，是指 id2 为该 id 的情况
4. 执行标注记录

    ```sh
    python 18_run_annotate.py
    ```

5. 进行 analysis，将非主体的 id 删除，同时这也是在查漏补缺，看看跟踪时有没有漏掉的 id（按 `a` 之后处理，按 `d` 删除，按 `q` 退出）

    ```sh
    python 26_filter_delete_id.py
    ```

6. 执行标注记录（由于 id 映射的问题，需要先从备份恢复至初始状态）

   ```shell
   ./25_cp_back.sh
   python 18_run_annotate.py
   ```

7. 检查结果有没有问题

    ```sh
    python 1_analysis.py
    ```

8. 如果出现重复 ID，按 `a` 替换左侧框为 `substitue_id`，按 `d` 替换右侧框为 `substitue_id`，按 `w` 删除上侧框，按 `s` 删除下侧框，按 `q` 退出

   ```sh
   python 7_quchong.py <substitue_id>
   ```

9. 备份标注文件

    ```shell
    python 0_backup.py
    ```

10. 切换标注视频

    ```shell
    # 切换前记得备份
    python 9_change_video.py
    ```

11. 视频内清洗完成后，进行视频间的 id 对齐（规则是 `id1->id2`）

    ```sh
    # 记录在 group_name/video_name/repla.txt 中
    python 3_replace_batch.py
    ```

12. 备份标注文件

    ```shell
    python 19_cp.py
    ```

13. 进行插值，大概 1 分半生成一个视频，可以生成完一个浏览一遍
    1. 对于G/G1/G2视频无需补全，按照max_missing_frames=15进行补全。
    2. 对于其他视角视频，按照max_missing_frames=30进行补全。

    ```shell
    ./24_inter_all.sh
    ```

    补全时，需要忽略的id还有帧范围都留成空表格，max_missing_frames按照上述要求设置，这种参数下的补全基本不会再出现偏移问题，**但补全后必须仔细检查视频，如果还是有偏移之类的问题，务必记录好有问题的ID填到表里，但无需再重新修改补全了，直接上传即可**。
    另外，单纯大量缺失的情况，不用再记录到表里了，只需要记录补全后出问题的ID。

14. 生成截图

    ```shell
    python 14_snapshot.py
    ```

15. 打包到 fine_labels

    ```shell
    python 15_pack.py
    ```

16. 上传到服务器

    ```shell
    ./16_upload.sh
    ```

17. 更新记录表

## 3_replace_batch

不要将 id 映射到它自身，会导致大量重复 id
