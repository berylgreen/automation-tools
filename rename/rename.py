import os
import configparser

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

# 获取文件夹路径
folder_path = config['settings']['folder_path']

# 遍历文件夹中的所有文件
for root, dirs, files in os.walk(folder_path):
    for file in files:
        old_file_path = os.path.join(root, file)

        # 找到第二个 "-" 的位置，并去掉其之前的所有字符
        parts = file.split('-')
        if len(parts) > 2:
            # 从第三部分开始拼接文件名
            new_file_name = '-'.join(parts[2:])
            new_file_path = os.path.join(root, new_file_name)

            # 重命名文件
            os.rename(old_file_path, new_file_path)
            print(f"Renamed: {old_file_path} -> {new_file_path}")
