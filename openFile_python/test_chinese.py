import zipfile
import os

def extract_zip_with_correct_encoding(zip_path, extract_to, encoding='gbk'):
    """
    解压zip文件，处理中文文件名乱码问题。

    :param zip_path: zip文件的路径
    :param extract_to: 解压到的目标目录
    :param encoding: zip文件中文件名的编码，默认为'gbk'
    """
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for zip_info in zip_ref.infolist():
            # 转换文件名编码
            zip_info.filename = zip_info.filename.encode('cp437').decode(encoding)
            # 确保目录存在
            if not os.path.exists(extract_to):
                os.makedirs(extract_to)
            # 解压文件
            zip_ref.extract(zip_info, extract_to)

# 示例用法
zip_path = 'data//124232022002_王洋_小球历险记.zip'  # zip文件路径
extract_to = 'output_dir'  # 解压目标目录
extract_zip_with_correct_encoding(zip_path, extract_to)