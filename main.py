import os
import hashlib
import csv
import shutil
import sys
from datetime import datetime

# ====================== 请修改这里的路径 ======================
ORIGIN_FILES_DIR = r"D:\【手机移出备份2026.06.15】\DCIM\Camera"   # 需要扫描的文件夹
STORAGE_DIR = r"E:\【NAS照片整理】"   # 信息库csv所在文件夹
STORAGE_FILE_DIR = r"E:\【NAS照片整理】\归档"   # 信息库csv所在文件夹
DB_FILENAME = "mao_file_index_db.csv"
ARCHIVE_DB_FILENAME = "mao_archive_file_index_db.csv"
DUPLICATE_NAME_DB_FILENAME = "mao_duplicated_name_file_index_db.csv"
COMPLETE_RECORD_FILENAME = "mao_record_completed_dir.csv"
# ============================================================

def compute_sha256(file_path: str, chunk_size=65536) -> str:
    """计算文件sha256，分块读取支持大文件"""
    sha256_obj = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                sha256_obj.update(chunk)
        return sha256_obj.hexdigest()
    except Exception as e:
        print(f"WARN - 读取文件失败 {file_path} : {e}")
        return ""

def load_known_database(db_dir: str, db_name: str) -> tuple[dict, set]:
    """从csv加载已知信息库，key:sha256, value: dict(path,size)"""
    known_db = {}
    known_filenames = set()
    db_path = os.path.join(db_dir, db_name)
    if not os.path.exists(db_path):
        print(f"INFO - 库文件不存在: {db_path}")
        return known_db, known_filenames

    try:
        # 主要为了兼容 Windows Excel：Excel 打开无 BOM 的 UTF‑8 csv 会乱码，带 BOM 才能正常显示中文
        with open(db_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                file_path = row.get("file_path", "")
                sha = row.get("sha256", "").strip()
                if not sha:
                    print(f"ERROR - 信息库损坏，SHA256值不存在: {file_path} - {row.get("file_size", "")}")
                    exit(-100)
                    # continue

                known_db[sha] = {
                    "path": file_path,
                    "size": int(row["file_size"])
                }

                basename = os.path.basename(file_path)
                known_filenames.add(basename)
    except Exception as e:
        print(f"ERROR - 读取信息库失败：{e}")
        exit(-200)

    return known_db, known_filenames

def load_duplicate_file_database(db_dir: str, db_name: str) -> dict:
    """从csv加载重名库，key:sha256, value: dict(path,size)"""
    duplicate_name_db = {}
    db_path = os.path.join(db_dir, db_name)
    if not os.path.exists(db_path):
        print(f"INFO - 重名库文件不存在: {db_path}")
        return duplicate_name_db

    try:
        # 主要为了兼容 Windows Excel：Excel 打开无 BOM 的 UTF‑8 csv 会乱码，带 BOM 才能正常显示中文
        with open(db_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                file_path = row.get("file_path", "")
                sha = row.get("sha256", "").strip()
                if not sha:
                    print(f"ERROR - 重名库损坏，SHA256值不存在: {file_path} - {row.get("file_size", "")}")
                    exit(-300)
                    # continue

                duplicate_name_db[sha] = {
                    "path": file_path,
                    "size": int(row.get("file_size", "")),
                    # "file_name": row.get("file_name", "")
                }
        print(f"INFO - 已加载重名库记录数：{len(duplicate_name_db)}")
    except Exception as e:
        print(f"ERROR - 读取重名库失败：{e}")
        exit(-500)

    return duplicate_name_db

def scan_all_files(root_dir: str):
    """遍历目录下所有文件，生成绝对路径"""
    for root, _, files in os.walk(root_dir):
        for name in files:
            fullpath = os.path.abspath(os.path.join(root, name))
            yield fullpath

def append_new_database(db_dir: str, db_name: str, new_db: dict) -> bool:
    """把新增信息库追加写入csv，不存在就写表头"""
    if not new_db:
        return False

    db_path = os.path.join(db_dir, db_name)
    file_exist = os.path.exists(db_path)

    with open(db_path, "a", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["file_path", "file_size", "sha256"])
        if not file_exist:
            writer.writeheader()
        for sha_val, item in new_db.items():
            writer.writerow({
                "file_path": item["path"],
                "file_size": item["size"],
                "sha256": sha_val
            })
    return True

def write_duplicate_name_db(db_dir: str, db_name: str, dup_db: dict):
    """写入文件名重名库，覆盖式写入（每次扫描生成完整结果）"""
    if not dup_db:
        print("INFO - 未发现重名新文件，无需写入")
        return

    db_path = os.path.join(db_dir, db_name)
    # file_exist = os.path.exists(db_path)

    with open(db_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["file_path", "file_size", "sha256"]) # , "file_name"
        # if not file_exist:
        #     writer.writeheader()
        writer.writeheader()
        for sha_val, item in dup_db.items():
            writer.writerow({
                "file_path": item["path"],
                "file_size": item["size"],
                "sha256": sha_val,
                # "file_name": item["file_name"]
            })
    print(f"INFO - 已覆写 {len(dup_db)} 条新记录到重名新文件库")

def record_completed_dir(db_dir: str, db_name: str, completed_dir: str):
    """写入已完成遍历信息库，追加式写入"""

    db_path = os.path.join(db_dir, db_name)
    file_exist = os.path.exists(db_path)

    with open(db_path, "a", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["dir_path", "date_time"])
        if not file_exist:
            writer.writeheader()
        writer.writerow({
            "dir_path": completed_dir,
            "date_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })
    print(f"INFO - 已追加根目录到已完成遍历信息库 - {completed_dir}")

def main_scan():
    input(f"按 3 次任意键开始处理：{ORIGIN_FILES_DIR}")
    input(f"按 2 次任意键开始处理：{ORIGIN_FILES_DIR}")
    input(f"按 1 次任意键开始处理：{ORIGIN_FILES_DIR}")
    print(f"INFO - 开始处理：{ORIGIN_FILES_DIR}")

    # 1.加载已知库，初始化新增库
    known_db, known_filenames = load_known_database(STORAGE_DIR, DB_FILENAME)
    print(f"INFO - 已加载信息库记录数：{len(known_db)}，已知文件名数量：{len(known_filenames)}")

    new_db = {}
    duplicate_name_db = load_duplicate_file_database(STORAGE_DIR, DUPLICATE_NAME_DB_FILENAME)

    new_file_count = 0
    duplicate_filename_new_file_count = 0
    skip_duplicate_filename_count = 0
    skip_duplicate_sha256_count = 0

    process = 0

    # 2.扫描BBB目录全部文件
    print(f"INFO - 开始扫描目录：{ORIGIN_FILES_DIR}")
    for file_abs in scan_all_files(ORIGIN_FILES_DIR):
        process += 1
        if process % 100 == 0:
            print(f"INFO - 正在处理第 {process} 个文件...")

        current_filename = os.path.basename(file_abs)

        try:
            file_size = os.path.getsize(file_abs)
        except Exception as e:
            print(f"WARN - 获取文件大小失败 {file_abs}: {e}")
            continue

        sha_hash = compute_sha256(file_abs)
        if not sha_hash:
            continue

        if current_filename in known_filenames:
            if sha_hash not in known_db and sha_hash not in new_db:
                if sha_hash not in duplicate_name_db:
                    # 重名文件的哈希值如果没有在已知库/新库中出现过，则加入重名库。目的是以后重命名保存，或者分类保存，因此记录不可丢失。
                    duplicate_name_db[sha_hash] = {
                        "path": file_abs,
                        "size": file_size,
                        # "file_name": current_filename
                    }
                    duplicate_filename_new_file_count += 1
                else:
                    # 重名文件的哈希值已被记录过，跳过不处理
                    skip_duplicate_filename_count += 1
            else:
                # 重名文件的哈希值已被记录过，跳过不处理
                skip_duplicate_filename_count += 1
        else:
            # 检查哈希是否在已知库 OR 新增库
            if sha_hash not in known_db and sha_hash not in new_db:
                new_db[sha_hash] = {
                    "path": file_abs,
                    "size": file_size
                }
                new_file_count += 1
            else:
                skip_duplicate_sha256_count += 1

    print(f"INFO - 扫描完成，"
          f"跳过重名哈希相同文件 {skip_duplicate_filename_count} 个，"
          f"跳过不重名哈希相同文件 {skip_duplicate_sha256_count} 个，"
          f"记录新文件 {new_file_count} 个，"
          f"记录重名新文件 {duplicate_filename_new_file_count} 个")

    # 3.追加保存新增数据
    ret = append_new_database(STORAGE_DIR, DB_FILENAME, new_db)
    if ret:
        print(f"INFO - 已追加 {len(new_db)} 条新记录到信息库")
    else:
        print("INFO - 未发现新文件，无需写入")


    # 4.输出文件名重名库（追加写入）
    write_duplicate_name_db(STORAGE_DIR, DUPLICATE_NAME_DB_FILENAME, duplicate_name_db)

    record_completed_dir(STORAGE_DIR, COMPLETE_RECORD_FILENAME, ORIGIN_FILES_DIR)
    print("INFO - 全部处理结束，完成！")

def main_copy_files():
    input(f"按 3 次任意键开始处理，数据库和文件归档目录：{STORAGE_DIR}")
    input(f"按 2 次任意键开始处理，数据库和文件归档目录：{STORAGE_DIR}")
    input(f"按 1 次任意键开始处理，数据库和文件归档目录：{STORAGE_DIR}")
    print(f"INFO - 开始处理：{STORAGE_DIR}")

    # 1.加载已知库
    print("INFO - 开始加载信息库...")
    known_db, _ = load_known_database(STORAGE_DIR, DB_FILENAME)
    print(f"INFO - 完成加载信息库，已索引 {len(known_db)} 个文件")

    print("INFO - 开始加载归档库...")
    archive_db, _ = load_known_database(STORAGE_DIR, ARCHIVE_DB_FILENAME)
    print(f"INFO - 完成加载归档库，已归档 {len(archive_db)} 个文件")

    if len(archive_db) > 0:
        input(f"按 3 次任意键开始处理，本次跳过已归档的 {len(archive_db)} 个文件")
        input(f"按 2 次任意键开始处理，本次跳过已归档的 {len(archive_db)} 个文件")
        input(f"按 1 次任意键开始处理，本次跳过已归档的 {len(archive_db)} 个文件")

    # new_archive_db = {}

    skip_file_count = 0
    copy_file_count = 0

    # 2.遍历信息库、增量拷贝、记录到新的归档库字典
    if not os.path.exists(STORAGE_FILE_DIR):
        os.makedirs(STORAGE_FILE_DIR)

    print(f"INFO - 开始增量拷贝...")

    for sha_val, item in known_db.items():
        src_file_path = item.get("path", None)
        src_file_size = item.get("size", None)
        if src_file_path is None:
            print("ERROR - 未读取到文件路径")
            exit(-1000)

        if sha_val in archive_db:
            skip_file_count += 1
            continue

        filename = os.path.basename(src_file_path)
        dst_file_path = os.path.join(STORAGE_FILE_DIR, filename)

        try:
            if not os.path.exists(src_file_path):
                print(f"ERROR - 源文件不存在：{src_file_path}")
                exit(-2000)

            if os.path.exists(dst_file_path):
                print(f"WARN - 目标文件已存在：{dst_file_path}")
                input("按 1 次任意键开始处理，即将覆盖文件：")

            shutil.copy2(src_file_path, dst_file_path)

        except FileNotFoundError as e:
            print(f"ERROR - 源文件不存在：{src_file_path} - {e}")
            exit(-3000)
        except shutil.SameFileError as e:
            print(f"ERROR - 源和目标是同一个文件：{src_file_path} -> {dst_file_path} - {e}")
            exit(-5000)
        except PermissionError as e:
            print(f"ERROR - 权限不足：{src_file_path} -> {dst_file_path} - {e}")
            exit(-6000)
        except KeyboardInterrupt as e:
            print(f"ERROR - ctrl-c 退出：{src_file_path} -> {dst_file_path} - {e}")
            exit(-8000)
        except BaseException as e:
            print(f"ERROR - 异常：{src_file_path} -> {dst_file_path} - {e}")
            exit(-9000)

        copy_file_count += 1

        new_archive_db = { sha_val: known_db[sha_val] }
        # new_archive_db[sha_val] = known_db[sha_val]
        append_new_database(STORAGE_DIR, ARCHIVE_DB_FILENAME, new_archive_db)

        print(f"\rINFO - 已归档文件： {len(archive_db) + copy_file_count}/{len(known_db)} ...", end="", flush=True)
        # if copy_file_count % 10 == 0:
        #     print(f"INFO - 已归档第 {copy_file_count} 个文件...")
    print("")

    print(f"INFO - 归档完成，"
          f"跳过已归档文件 {skip_file_count} 个，"
          f"本次新归档文件 {copy_file_count} 个，"
          f"总计已归档文件 {skip_file_count + copy_file_count} 个，"
          f"信息库索引文件 {len(known_db)} 个")

    # 3.追加保存新增数据
    # ret = append_new_database(STORAGE_DIR, ARCHIVE_DB_FILENAME, new_archive_db)
    # if ret:
    #     print(f"INFO - 已追加 {len(new_archive_db)} 条新记录到归档库")
    # else:
    #     print("INFO - 未归档新文件，无需写入")

    print("INFO - 全部处理结束，完成！")


if __name__ == "__main__":

    print("1. 扫描建库")
    print("2. 按库增量拷贝")

    feature = input("请输入功能编号：")

    if feature == "1":
        if len(sys.argv) < 2:
            print("ERROR - 输入需要检查的目录名")
            exit(-1)
        ORIGIN_FILES_DIR = sys.argv[1]
        main_scan()
    elif feature == "2":
        main_copy_files()
    else:
        print(f"输入不正确，{feature}")

