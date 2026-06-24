import configparser
import re
import shutil
from collections import defaultdict
from pathlib import Path
import time

def read_text_file(file_path):
    """
    读取并返回文本文件内容，尝试使用 utf-8 和 gbk 编码。
    """
    path = Path(file_path)
    if not path.exists():
        print(f"配置文件中指定的文本文件不存在: {file_path}")
        return ""
    try:
        return path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding='gbk')
        except Exception as e:
            print(f"读取名单文件失败: {e}")
            return ""

def extract_numbers_after(filename, start_string):
    """
    从文件名中提取以指定起始字符串开头后面的字符串。
    """
    index_start = filename.find(start_string)
    if index_start != -1:
        return start_string + filename[index_start + len(start_string):]
    return filename

def extract_numbers(filename, pattern):
    """
    使用预编译的正则表达式提取文件名中的学号。
    如果没找到返回 None。
    """
    match = pattern.search(filename)
    if match:
        return match.group()
    return None

def create_folder(base_path, output_key):
    """
    在与 base_path 同级的目录下创建输出文件夹。
    如果文件夹已存在，则清空其中的文件。
    """
    base = Path(base_path)
    output_folder_name = f"{Path(output_key).name}_{base.name}"
    # 确保在源文件夹的同级目录创建，不污染源文件夹内部
    output_path = base.parent / output_folder_name
    
    if not output_path.exists():
        output_path.mkdir(parents=True)
    else:
        # 清空已有输出文件夹的内容
        for item in output_path.iterdir():
            try:
                if item.is_file() or item.is_symlink():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            except Exception as e:
                print(f"清空输出目录文件失败 {item}. 错误原因: {e}")
    return output_path

def main():
    config = configparser.ConfigParser()
    config_path = Path('config.ini')
    if not config_path.exists():
        print("未找到 config.ini 文件，请确保在脚本同级目录存在该文件。")
        return

    config.read(config_path, encoding='utf-8')
    
    # ---------------- 1. 读取配置 ----------------
    source_dir_str = config['Directory'].get('source_dir', '')
    student_id_list_file = config['Directory'].get('student_id_list_file', '')
    output_dir_name = config['Directory'].get('output_dir_name', 'output')
    
    target_extensions_str = config['FileRules'].get('target_extensions', '')
    student_id_prefix = config['FileRules'].get('student_id_prefix', '')
    
    check_mixed_ids = config.getboolean('Tasks', 'check_mixed_ids', fallback=True)
    check_duplicate_ids = config.getboolean('Tasks', 'check_duplicate_ids', fallback=True)
    delete_unmatched_files = config.getboolean('Tasks', 'delete_unmatched_files', fallback=False)

    source_dir = Path(source_dir_str)
    
    if not source_dir.exists() or not source_dir.is_dir():
        print(f"配置的待处理文件夹路径不存在或不是一个文件夹: {source_dir}")
        return
        
    # 安全解析需要收集的扩展名，例如从 ".docx/.pdf" 转换为 (".docx", ".pdf")
    # 并且统一转换为小写，便于后续无视大小写的比较
    target_extensions = tuple(ext.strip().lower() for ext in target_extensions_str.split('/') if ext.strip())
    
    # 预编译提取学号的正则表达式，提升性能
    pattern = re.compile(f"{re.escape(student_id_prefix)}\\d+")
    
    # 读取预期的学生名单
    text_data = read_text_file(student_id_list_file)
    expected_student_ids = set(re.findall(r'\d+', text_data))
    
    print("\n[1/4] 开始扫描文件目录...")
    
    # ---------------- 2. 单次全量扫描（Single-pass Scan） ----------------
    # 根据所在的立即父级目录进行分组：{目录对象: [文件1, 文件2, ...]}
    subfolder_files = defaultdict(list)
    # 不匹配的冗余文件列表
    unconfigured_files = []
    
    # 获取输出文件夹名称，避免如果它不小心建在了源文件夹内部而被误删或递归读取
    output_folder_name_to_avoid = f"{Path(output_dir_name).name}_{source_dir.name}"
    
    for item in source_dir.rglob('*'):
        if item.is_file():
            # 过滤掉输出文件夹，防止嵌套导致的死循环和污染
            if output_folder_name_to_avoid in item.parts:
                continue
                
            # 判断扩展名
            if target_extensions and not item.name.lower().endswith(target_extensions):
                unconfigured_files.append(item)
            else:
                subfolder_files[item.parent].append(item)
                
    # ---------------- 3. 删除无关文件 ----------------
    if target_extensions and delete_unmatched_files:
        print(f"\n[2/4] 执行删除未配置类型的文件 (总计 {len(unconfigured_files)} 个)...")
        for item in unconfigured_files:
            try:
                item.unlink()
                print(f"  [-] 已删除非配置类型文件: {item}")
            except Exception as e:
                print(f"  [x] 删除文件失败: {item}, 错误原因: {e}")
    else:
        print(f"\n[2/4] 跳过删除未配置类型的文件（配置未启用，发现了 {len(unconfigured_files)} 个无关文件）。")

    # ---------------- 4. 逻辑校验与报告 ----------------
    print("\n[3/4] 运行数据与名单校验...")
    different_student_files = []  # 同目录混杂了不同学号
    same_student_files = []       # 同目录出现了同名学号
    multiple_files_in_folder = [] # 同目录有多个目标文件
    
    found_student_ids = set()
    
    for subfolder, files in subfolder_files.items():
        if len(files) > 1:
            multiple_files_in_folder.extend(files)
            
        student_files_dict = defaultdict(list)
        for file in files:
            student_id = extract_numbers(file.name, pattern)
            if student_id:
                student_files_dict[student_id].append(file)
                found_student_ids.add(student_id)
                
        # 检查混合学号（同一文件夹存在不同学号的文件）
        if len(student_files_dict.keys()) > 1:
            for file_list in student_files_dict.values():
                different_student_files.extend(file_list)
                
        # 检查重复学号（同一文件夹下同一个学号有多个文件）
        for file_list in student_files_dict.values():
            if len(file_list) > 1:
                same_student_files.extend(file_list)
                
    missing_numbers = expected_student_ids - found_student_ids
    no_record_numbers = found_student_ids - expected_student_ids
    
    print("\n========== 扫描报告 ==========")
    print(f"预期学号总数: {len(expected_student_ids)}")
    print(f"成功提取学号: {len(found_student_ids)}")
    print(f"未收到文件数: {len(missing_numbers)}")
    
    if missing_numbers:
        print(f"\n未收到以下学号文件（共{len(missing_numbers)}个）：")
        print(sorted(list(missing_numbers)))
    
    if no_record_numbers:
        print(f"\n无记录文件（提取出的学号不在名单中，共{len(no_record_numbers)}个）：")
        print(sorted(list(no_record_numbers)))
        
    if check_mixed_ids and different_student_files:
        print(f"\n警告: 同一个子文件夹中混杂了多个不同学号的文件！")
        for f in different_student_files:
            print(f"  - {f}")
            
    if check_duplicate_ids:
        if same_student_files:
            print(f"\n警告: 同一个子文件夹中存在多个提取为【同一学号】的文件！")
            for f in same_student_files:
                print(f"  - {f}")
        
        if multiple_files_in_folder:
            print(f"\n警告: 同一个子文件夹中存在多个目标文件！")
            for f in multiple_files_in_folder:
                print(f"  - {f}")
                
    if not check_mixed_ids and not check_duplicate_ids:
        print("\n注：学号混杂及重复学号检查未启用。")
    print("==============================\n")

    # ---------------- 5. 拷贝与重命名 ----------------
    print("[4/4] 准备输出文件...")
    output_folder = create_folder(source_dir_str, output_dir_name)
    
    copy_count = 0
    for files in subfolder_files.values():
        for file in files:
            new_file_name = extract_numbers_after(file.name, student_id_prefix)
            destination_file_path = output_folder / new_file_name
            try:
                shutil.copy2(file, destination_file_path)
                copy_count += 1
            except Exception as e:
                print(f"文件拷贝失败: {file} -> {destination_file_path}. 原因: {e}")
            
    print(f"所有操作已完成！成功提取并拷贝 {copy_count} 个文件至: \n{output_folder}")

if __name__ == "__main__":
    main()
