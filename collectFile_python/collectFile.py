import os
import re
import shutil
import configparser
#from docx import Document
#from docx2pdf import convert
from collections import defaultdict
import time

def delete_unconfigured_files(folder_path, allowed_extensions):
    """
    删除未在配置中指定的后缀名的文件。
    """
    extensions = allowed_extensions.split('/')
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if not any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)  # 删除文件
                    print(f"已删除非配置类型文件: {file_path}")
                except Exception as e:
                    print(f"删除文件失败: {file_path}, 错误原因: {e}")

def find_files_with_extension(folder_path, file_extensions):
    """
    Search for all files with specific extensions within a specified directory and return their paths.
    Extensions should be provided as a string separated by slashes, e.g., '.txt/.pdf/.docx'.
    """
    extensions = file_extensions.split('/')
    files_with_extension = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                files_with_extension.append(os.path.join(root, file))
    return files_with_extension

def extract_numbers_after(file, start_string):
    """
    从文件名中提取以指定起始字符串开头后面的字符串。
    """
    #numbers = re.findall(r'{0}\w+'.format(start), filename)

    # 从文件名中找到指定起始字符串的索引位置
    index_start = file.find(start_string)
    if index_start != -1:
        # 构建新的文件名，保留指定起始字符串这部分字符
        number_after = start_string + file[index_start + len(start_string):]
    else:
        number_after = file  # 如果文件名中没有指定起始字符串，保持原文件名不变
        print(number_after)
    return number_after
    
def extract_numbers(filename, start):
    """
    从文件名中提取以指定起始字符串开头的数字。
    """
    #last_backslash_index = filename.rfind('\\')
    #if last_backslash_index == -1:
    #    return None  # 如果找不到反斜杠，返回None
    # 从最后一个反斜杠后面的部分提取数字
    #numbers = re.findall(r'\b\w?{0}\d+'.format(start), filename[last_backslash_index + 1:])
    numbers = re.findall(r'{0}\d+'.format(start), filename)
    if numbers:
        return numbers[0]  # 返回第一次匹配到的编号
    else:
        #print(filename)
        return filename

def read_text_file(file_path):
    """
    Read and return the content of a text file, trying different encodings if necessary.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = file.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='gbk') as file:
            data = file.read()
    return data

def find_missing_numbers(folder_path, text_file_path, file_extension, start_string):
    """
    在指定文件夹中查找指定后缀名的文件的编号，然后与文本文件中的编号进行比较，找出缺失的编号。
    """
    # 读取文本文件中的编号
    text_data = read_text_file(text_file_path)
    text_numbers = re.findall(r'\d+', text_data)
    # 获取文件夹中的所有指定后缀名的文件路径
    files_with_extension = find_files_with_extension(folder_path, file_extension)
    print(f"All {file_extension} files found:")
    # 提取指定后缀名文件中的start_string后面的字符串
    file_numbers_after = [extract_numbers_after(file, start_string) for file in files_with_extension]
    #file_numbers_after.sort()
    #for file in file_numbers_after:
    #    print(file)
    # 提取指定后缀名文件中的编号
    file_numbers = [extract_numbers(file, start_string) for file in file_numbers_after if extract_numbers(file, start_string) is not None]
     
    #file_numbers.sort()  # 对指定后缀名文件中的编号列表进行排序
#打印排序后的所有学号
    #for file in file_numbers:
        #print(file)

    # 找出文本文件中存在但指定后缀名文件中缺失的编号
    missing_numbers = [number for number in text_numbers if number not in file_numbers]
    
    # 找出指定后缀名文件的无记录文件名
    no_record_numbers = [number for number in file_numbers if number not in text_numbers]
    print(f"无学号记录文件：", no_record_numbers)  
    return missing_numbers


def check_same_student_id(folder_path, start_string):
    """
    检查同一个子文件夹中是否存在两个以上的文件，并输出到列表。
    """
    different_student_files = []
    for root, dirs, files in os.walk(folder_path):
        files_dict = defaultdict(list)
        for file in files:
            # 提取文件名中的学号部分
            student_id = extract_numbers(file, start_string)
            if student_id:
                # 将文件按学号分类
                files_dict[student_id].append(os.path.join(root, file))
        
        # 检查是否有同一个学号对应多个文件
        for student_id, file_list in files_dict.items():
            if len(file_list) > 1:
                different_student_files.extend(file_list)
    
    return different_student_files
"""
def check_different_student_ids(folder_path):
    
    #检查同一个子文件夹中是否存在两个以上不同学号的文件，并输出到列表。
    
    student_files_dict = defaultdict(set)
    different_student_files = []

    # 遍历文件夹中的所有文件
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # 提取文件名中的学号部分
            student_id = extract_numbers(file, start_string)
            if student_id:
                # 将文件路径添加到对应学号的集合中
                student_files_dict[student_id].add(os.path.join(root, file))
                print(student_files_dict)

    # 检查是否存在两个以上不同学号的文件
    for student_id, file_set in student_files_dict.items():
        if len(file_set) > 1:
            different_student_files.extend(file_set)

    return different_student_files
"""
def check_different_student_ids(folder_path, start_string):
    """
    检查同一个子文件夹中是否存在两个以上不同学号的文件，并输出到列表。
    """
    different_student_files = []
    multiple_files = []

    # 获取folder_path下一层级的子文件夹列表
    subfolders = [f.path for f in os.scandir(folder_path) if f.is_dir()]

    for subfolder in subfolders:
        student_files_dict = defaultdict(set)

        # 遍历子文件夹中的所有文件
        for root, dirs, files in os.walk(subfolder):
            for file in files:
                # 提取文件名中的学号部分
                student_id = extract_numbers(file, start_string)
                if student_id:
                    # 将文件路径添加到对应学号的集合中
                    student_files_dict[student_id].add(os.path.join(root, file))

        # 检查是否存在两个以上不同学号的文件
        if len(student_files_dict.keys()) > 1:
            for student_id, file_set in student_files_dict.items():
                 different_student_files.extend(list(file_set))

    return different_student_files

def check_multiple_files(folder_path):
    """
    检查同一个子文件夹中是否存在两个以上的文件，并输出到列表。
    """
    multiple_files = []

    # 遍历文件夹中的所有文件
    for root, dirs, files in os.walk(folder_path):
        if len(files) > 1:
            multiple_files.extend([os.path.join(root, file) for file in files])

    return multiple_files


def find_files_with_extension(folder_path, file_extensions):
    """
    Finds all files with specific extensions within a given directory.
    """
    file_list = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(tuple(file_extensions)):
                file_list.append(os.path.join(root, file))
    return file_list


def create_folder(base_path,output_key):
    """
    Creates a folder at the specified path. If the folder already exists, clears its contents.
    """
    output_folder_name = os.path.basename(output_key) + '_' + os.path.basename(base_path)
    # 构建输出文件夹的路径
    output_path = os.path.join(os.path.dirname(base_path), output_folder_name)
    # Create the folder if it doesn't exist
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    # If the folder exists, clear its contents
    else:
        for filename in os.listdir(output_path):
            file_path = os.path.join(output_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
    return output_path

def copy_and_rename_files(base_path, file_extensions, start_string, output_key="output"):
    output_folder = create_folder(base_path,output_key)
    # 遍历文件夹中的所有文件
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if any(file.endswith(ext) for ext in file_extensions):
                # 构建源文件路径和目标文件路径
                source_file_path = os.path.join(root, file)
                #目标文件名是学号后面的字符串
                new_file_name=extract_numbers_after(file,start_string)
                #目标文件路径                
                destination_file_path = os.path.join(output_folder, new_file_name)

                # 拷贝文件并重命名，保留文件的元数据
                shutil.copy2(source_file_path, destination_file_path)
                #print(f"File copied and renamed: {new_file_name}")
                #convert_word_to_pdf(output_folder, pdf_folder)

def convert_word_to_pdf(base_path, pdf_key):
    """
    Converts all Word documents (.docx) in the output_folder to PDF and saves them in pdf_folder_path.
    """
    time.sleep(10)  # 暂停1秒
    pdf_folder_path = create_folder(base_path,pdf_key)
    docx_files = find_files_with_extension(base_path, ".docx")
    for docx_file in docx_files:
        base_name = os.path.basename(docx_file)
        pdf_file = os.path.join(pdf_folder_path, os.path.splitext(base_name)[0] + ".pdf")
        # Using docx2pdf library to convert docx to pdf
        #convert(docx_file, pdf_file)

if __name__ == "__main__":
    config = configparser.ConfigParser()
    # 使用UTF-8编码打开配置文件
    with open('config.ini', 'r', encoding='utf-8') as configfile:
        config.read_file(configfile)
    
    source_dir = config['Paths']['source_dir']
    student_id_list_file = config['Paths']['student_id_list_file']
    target_extensions = config['Paths']['target_extensions']
    student_id_prefix = config['Params']['student_id_prefix']
    output_dir_name = config['Paths']['output_dir_name']
    pdf_dir_name = config['Paths']['pdf_dir_name']
    
    check_mixed_ids = config.getboolean('Params', 'check_mixed_ids')
    check_duplicate_ids = config.getboolean('Params', 'check_duplicate_ids')
    delete_unmatched_files = config.getboolean('Params', 'delete_unmatched_files', fallback=False)

    # 检查路径是否存在
    if not os.path.exists(source_dir):
        print(f"路径不存在: {source_dir}")
        # 这里可以加入访问该路径的代码
    
    # 删除未在 target_extensions 中配置的文件类型
    if target_extensions and delete_unmatched_files:
        delete_unconfigured_files(source_dir, target_extensions)


    # 这里可以加入错误处理代码或其他逻辑
    copy_and_rename_files(source_dir, target_extensions, student_id_prefix, output_dir_name)
    missing_numbers = find_missing_numbers(source_dir, student_id_list_file, target_extensions, student_id_prefix)
        
    print(f"未收到以下学号文件：", missing_numbers)
    print("未收到文件数:", len(missing_numbers))

    if check_mixed_ids:
        
        # 检查同一个子文件夹中是否存在两个以上不同学号的文件，并输出到列表
        different_student_files = check_different_student_ids(source_dir, student_id_prefix)
        print("\n同一个子文件夹中存在两个以上不同学号的文件：")
        for file in different_student_files:
            print(file)


    if check_duplicate_ids:

        same_student_files = check_same_student_id(source_dir, student_id_prefix)
        print("同一个子文件夹中存在两个以上相同学号的文件：")
        for file in same_student_files:
            print(file)
  

        # 检查同一个子文件夹中是否存在两个以上的文件，并输出到列表
        multiple_files = check_multiple_files(source_dir)
        print("\n同一个子文件夹中存在两个以上的文件：")
        for file in multiple_files:
            print(file)      
            
    else:
        print("Checking for same student IDs is not enabled.")

 
    

