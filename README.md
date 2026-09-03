# Photo-Storage-Manager

# 1. Scan files, compute sha256, and record the info of files.

```
uv run .\main.py <your-first-directory>

uv run .\main.py F:\Robin合影
```

<img width="1109" height="402" alt="image" src="https://github.com/user-attachments/assets/c655d8e0-860f-4918-8702-0da3f31e6eee" />

```
PS E:\MaoDev\MaoPhotoStorageManager> uv run .\main.py F:\Robin合影
1. 扫描建库
2. 按库增量拷贝
请输入功能编号: 1
按 3 次任意键开始处理: F:\Robin合影
按 2 次任意键开始处理: F:\Robin合影
按 1 次任意键开始处理: F:\Robin合影
INFO - 开始处理: F:\Robin合影
INFO - 库文件不存在: R:\\mao_file_index_db.csv
INFO - 已加载信息库记录数: 0, 已知文件名数量: 0
INFO - 重名库文件不存在: R:\\mao_duplicated_name_file_index_db.csv
INFO - 开始扫描目录: F:\Robin合影
INFO - 扫描完成，跳过重名哈希相同文件 0 个，跳过不重名哈希相同文件 0 个，记录新文件 9 个，记录重名新文件 0 个
INFO - 已追加 9 条新记录到信息库
INFO - 未发现重名新文件，无需写入
INFO - 已追加根目录到已完成遍历信息库 - F:\Robin合影
INFO - 全部处理结束，完成！

PS E:\MaoDev\MaoPhotoStorageManager>
```

## Incremental processing

```
uv run .\main.py <your-next-directory>

uv run .\main.py F:\Robin合影
```

<img width="1136" height="384" alt="image" src="https://github.com/user-attachments/assets/2fef76ab-4367-4114-b9aa-27066e51494a" />

```
PS E:\MaoDev\MaoPhotoStorageManager> uv run .\main.py F:\Robin合影
1. 扫描建库
2. 按库增量拷贝
请输入功能编号：1
按 3 次任意键开始处理：F:\Robin合影
按 2 次任意键开始处理：F:\Robin合影
按 1 次任意键开始处理：F:\Robin合影
INFO - 开始处理：F:\Robin合影
INFO - 已加载信息库记录数：9，已知文件名数量：9
INFO - 重名库文件不存在：R:\\mao_duplicated_name_file_index_db.csv
INFO - 开始扫描目录：F:\Robin合影
INFO - 扫描完成，跳过重名哈希相同文件 9 个，跳过不重名哈希相同文件 0 个，记录新文件 0 个，记录重名新文件 0 个
INFO - 未发现新文件，无需写入
INFO - 未发现重名新文件，无需写入
INFO - 已追加根目录到已完成遍历信息库 - F:\Robin合影
INFO - 全部处理结束，完成！
PS E:\MaoDev\MaoPhotoStorageManager>
```

# 2. Copy and archiving the files incrementally

```
uv run .\main.py
```

<img width="713" height="314" alt="image" src="https://github.com/user-attachments/assets/34ce3244-5933-4191-a4e7-777b73b1f6c3" />

```
PS E:\MaoDev\MaoPhotoStorageManager> uv run .\main.py
1. 扫描建库
2. 按库增量拷贝
请输入功能编号：2
按 3 次任意键开始处理，数据库和文件归档目录：E:\【NAS照片整理】
按 2 次任意键开始处理，数据库和文件归档目录：E:\【NAS照片整理】
按 1 次任意键开始处理，数据库和文件归档目录：E:\【NAS照片整理】
INFO - 开始处理：E:\【NAS照片整理】
INFO - 开始加载信息库...
INFO - 完成加载信息库，已索引 11841 个文件
INFO - 开始加载归档库...
INFO - 库文件不存在: E:\【NAS照片整理】\mao_archive_file_index_db.csv
INFO - 完成加载归档库，已归档 0 个文件
INFO - 开始增量拷贝...
INFO - 已归档文件： 3106/11841 ...
```
