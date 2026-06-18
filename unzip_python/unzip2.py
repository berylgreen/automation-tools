import os
import zipfile
import rarfile
#import py7zr
import shutil
from pathlib import Path

def extract_zip_with_correct_encoding(zip_path, extract_to):
    """
    解压zip文件，处理中文文件名乱码问题。

    :param zip_path: zip文件的路径
    :param extract_to: 解压到的目标目录
    :param encoding: zip文件中文件名的编码，默认为'gbk'
    """
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for zip_info in zip_ref.infolist():
            # 转换文件名编码
            try:
                zip_info.filename = zip_info.filename.encode('cp437').decode('gbk')
            except Exception as e:
                zip_info.filename = zip_info.filename.encode('gbk').decode('gbk')
                print(f"发生错误: {e}")

            # 确保目录存在
            if not os.path.exists(extract_to):
                os.makedirs(extract_to)
            # 解压文件
            zip_ref.extract(zip_info, extract_to)


# 定义解压函数
def extract_zip(file_path, extract_to):
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def extract_rar(file_path, extract_to):
   with rarfile.RarFile(file_path) as rar_ref:
       rar_ref.extractall(extract_to)

def unzip_to_same_directory(file_path,extract_to):
    # 获取压缩包所在目录
    dir_path = os.path.dirname(file_path)
    # 解压缩目标文件夹与压缩包同级
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(dir_path)

#def extract_7z(file_path, extract_to):
#    with py7zr.SevenZipFile(file_path, mode='r') as zf:
#        zf.extractall(path=extract_to)

# 获取解压文件夹中的内容数量
def get_files_in_directory(directory):
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

def get_folders_in_directory(directory):
    return [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]

# 主函数
def process_compressed_files(data_dir, output_dir, extract_to_same_folder=False):
    # 如果输出文件夹不存在，创建它
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 遍历data目录下的所有压缩文件
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith('.zip'):
                if extract_to_same_folder:
                    extract_func = unzip_to_same_directory
                else:
                    extract_func = extract_zip_with_correct_encoding

            elif file.endswith('.rar'):
                extract_func = extract_rar
            #elif file.endswith('.7z'):
            #    extract_func = extract_7z
            else:
                continue

            # 创建一个临时目录来解压文件
            temp_dir = os.path.join(output_dir, 'temp')
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            # 解压文件
            extract_func(file_path, temp_dir)

            # 获取解压出来的内容
            files_in_temp = get_files_in_directory(temp_dir)
            folders_in_temp = get_folders_in_directory(temp_dir)

            # 判断temp文件夹中的内容数量
            if len(files_in_temp) + len(folders_in_temp) == 1:
                # 如果只有一个文件或文件夹，直接将内容移动到data_output文件夹
                target_folder = output_dir
                if not os.path.exists(target_folder):
                    os.makedirs(target_folder)

                # 移动所有解压出的内容
                for item in os.listdir(temp_dir):
                    shutil.move(os.path.join(temp_dir, item), target_folder)

            elif len(files_in_temp) + len(folders_in_temp) > 1:
                # 如果temp文件夹中有多个文件或文件夹
                target_folder_name = os.path.splitext(file)[0]  # 使用压缩包文件名作为新文件夹的名字
                target_folder = os.path.join(output_dir, target_folder_name)

                if not os.path.exists(target_folder):
                    os.makedirs(target_folder)

                # 移动所有解压出的内容到目标文件夹
                for item in os.listdir(temp_dir):
                    shutil.move(os.path.join(temp_dir, item), target_folder)

            # 清理临时解压目录
            shutil.rmtree(temp_dir)

# 设置data目录和output目录
data_directory = 'data_output'
output_directory = data_directory + '_output'
# 设置是否解压到与压缩包相同的文件夹
extract_to_same_folder = True
# 运行主函数
process_compressed_files(data_directory, output_directory, extract_to_same_folder)
