import os
import subprocess
import sys
from configparser import ConfigParser
import time
import re
# 打开图片文件
def open_image_file(file_path):
    try:
        program_path = r'C:\Program Files\Honeyview\Honeyview.exe'
        process = subprocess.Popen([program_path, file_path], shell=True)
        print(f"打开文件: {file_path}")
    except Exception as e:
        print(f"打开文件时出现错误: {e}")

def open_max_file(file_path):
    try:
        program_path = r'D:\Program Files\Autodesk\3ds Max 2022\3dsmax.exe'
        process = subprocess.Popen([program_path, file_path], shell=True)
        print(f"打开文件: {file_path}")
    except Exception as e:
        print(f"打开文件时出现错误: {e}")

def open_video_file(file_path):
    try:
        program_path = r'D:\Program Files\PotPlayer\PotPlayerMini.exe'
        process = subprocess.Popen([program_path, file_path], shell=True)
        print(f"打开文件: {file_path}")
    except Exception as e:
        print(f"打开文件时出现错误: {e}")
def open_word_file(file_path):
    try:
        #用wps打开word文件
        program_path = r'C:\Users\chenc\AppData\Local\Kingsoft\WPS Office\12.1.0.21541\office6\WPS.exe'
        process = subprocess.Popen([program_path, file_path], shell=True)
        print(f"打开文件: {file_path}")
    except Exception as e:
        print(f"打开文件时出现错误: {e}")
        #用win32com.client打开word文件
        program_path = r'C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE'
        process = subprocess.Popen([program_path, file_path], shell=True)
        print(f"打开文件: {file_path}")

def close_files():
    # 关闭上一份文件
    with open('closeFiles.py', 'r', encoding='utf-8') as fileclose:
        exec(fileclose.read())

# 根据命令行参数调整学号
def adjust_student_id(student_id, studentid_change_mode):
   return str(int(student_id) + int(studentid_change_mode)  )

# 更新配置文件中的学号
def update_student_id_in_config(config,new_student_id):
    config.set('Settings', 'student_id', str(new_student_id))
    with open('open_config'
              '.ini', 'w', encoding='utf-8') as config_file:
        config.write(config_file)


def open_files_by_id(base_path, file_types, student_id, filename_filter_enable, text_data_zhuti):
    # 找出base_path下所有根目录
    root_dirs = [os.path.join(base_path, name) for name in os.listdir(base_path) if
                 os.path.isdir(os.path.join(base_path, name))]
    # 遍历所有根目录
    for root_dir in root_dirs:
        # 如果root_dir不包含字符串student_id， 则跳过该目录
        if student_id not in root_dir:
            continue
        # 遍历所有文件
        for root, dirs, files in os.walk(root_dir):
            #标记已经打开过image文件
            has_opened_image = 0
            print(files)
            for file in files:
                if filename_filter_enable:
                    # 判断文件是否包含student_id
                    # 或者判断文件名是否包括有列表中的一个
                    if student_id not in file and not any(keyword in file for keyword in text_data_zhuti):
                        continue
                # 判断文件后缀
                if file.endswith('.max') and '.max' in file_types:
                    open_max_file(os.path.join(root, file))
                elif (file.endswith(('.jpg', '.JPG', '.jpeg', '.JPEG', '.png', '.PNG', '.gif', '.GIF'))
                      and '.jpg' in file_types
                      and has_opened_image <1):
                    open_image_file(os.path.join(root, file))
                    has_opened_image+=1
                elif file.endswith(('.mp4', '.avi')) and '.mp4' in file_types:
                    # 打开文件
                    open_video_file(os.path.join(root, file))
                elif file.endswith('.docx') and '.docx' in file_types:
                    # 打开文件
                    open_word_file(os.path.join(root, file))

                else:
                    # 其他文件类型，不处理
                    pass


def read_text_file_line(file_path):
    """
    Read and return the content of a text file, trying different encodings if necessary.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='gbk') as file:
            lines = file.readlines()
    lines = [line.rstrip() for line in lines]#for循环读取每行，并去掉结尾的换行符

    return lines
# 主函数
def main():
    #关闭旧文件
    close_files()
    #休眠2秒,防止文件刚被打开就被关闭了
    time.sleep(1)

    # 加载配置文件
    config = ConfigParser()
    config.read('open_config.ini', encoding='utf-8')
    base_path = config.get('Settings', 'base_path')
    file_types = config.get('Settings', 'file_types').split('/')  # 以"/"分隔的文件类型
    filename_filter_enable = config.getboolean('Settings','filename_filter_enable')
    check_class_enable = config.getboolean('Settings', 'check_class_enable')
    base_path_2 = config.get('Settings', 'base_path_2')
    file_types_2 = config.get('Settings', 'file_types_2').split('/')  # 以"/"分隔的文件类型   student_id = config.get('Settings', 'student_id')
    filename_filter_enable_2 = config.getboolean('Settings','filename_filter_enable_2')
    student_id = config.get('Settings','student_id')
    student_id_change_mode = config.get('Settings','student_id_change_mode')
    data_file_mode_enable = config.getboolean('Settings','data_file_mode_enable')
    stu_ids_file_path = config.get('Settings', 'stu_ids_file_path')
    stu_zhuti_file_path = config.get('Settings', 'stu_zhuti_file_path')

    print(f"文件路径: {base_path}")
    if check_class_enable:
        print(f"文件路径: {base_path_2}")
    #将data_file_mode_enable字符串转为布尔值
    #读取专升本主题文件
    text_data_zhuti = read_text_file_line(stu_zhuti_file_path)
    #去除空行
    text_data_zhuti = [s for s in text_data_zhuti if s != '']
    print(text_data_zhuti)

    if data_file_mode_enable :
        # 读取文本文件中的编号
        text_numbers = read_text_file_line(stu_ids_file_path)
        for line in text_numbers:
            student_id=line.strip()
            open_files_by_id(base_path, file_types, student_id,filename_filter_enable,text_data_zhuti)
            if check_class_enable:
                open_files_by_id(base_path_2, file_types_2, student_id,filename_filter_enable_2,text_data_zhuti)#打开课堂考察
            #等待输入
            input("按任意键继续...")
            #关闭旧文件
            close_files()
            #休眠2秒,防止文件刚被打开就被关闭了
            time.sleep(1)
    else:
        open_files_by_id(base_path, file_types, student_id,filename_filter_enable,text_data_zhuti)
        if check_class_enable:
            open_files_by_id(base_path_2, file_types_2, student_id,filename_filter_enable_2,text_data_zhuti)#打开课堂考察
        #调整学号
        student_id = adjust_student_id(student_id, student_id_change_mode)
        update_student_id_in_config(config,student_id)

if __name__ == "__main__":
    main()
