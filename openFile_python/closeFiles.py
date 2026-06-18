import subprocess
import configparser
import win32com.client

def close_honeyview():
    try:
        subprocess.Popen("taskkill /IM Honeyview.exe /F", shell=True)
        print("Honeyview已被强制关闭。")
    except subprocess.CalledProcessError as e:
        print(f"尝试关闭Honeyview时出错：返回代码 {e.returncode}")
    except Exception as e:
        print(f"关闭Honeyview时遇到错误：{e}")

def close_3ds_max():
    try:
        subprocess.Popen("taskkill /IM 3dsmax.exe /F", shell=True)
        print("3ds Max已被强制关闭。")
    except subprocess.CalledProcessError as e:
        print(f"尝试关闭3ds Max时出错：返回代码 {e.returncode}")
    except Exception as e:
        print(f"关闭3ds Max时遇到错误：{e}")

def close_docx():
    try:
        # Connect to the running instance of Word
        word = win32com.client.Dispatch("Word.Application")
        word.Quit()  # Quit Word without saving
        print("Word文档已被关闭，没有保存任何更改。")
    except Exception as e:
        print(f"关闭Word文档时遇到错误：{e}")

def close_docx_force():
    try:
        # Connect to the running instance of Word
        subprocess.Popen("taskkill /IM winword.exe /F", shell=True)
        print("Word已被强制关闭。")
    except Exception as e:
        print(f"关闭Word文档时遇到错误：{e}")

def close_potplayer():
    try:
        # Close PotPlayer (which handles .mp4 and .avi files)
        subprocess.Popen("taskkill /IM PotPlayerMini.exe /F", shell=True)
        print("PotPlayer已被强制关闭。")
    except subprocess.CalledProcessError as e:
        print(f"尝试关闭PotPlayer时出错：返回代码 {e.returncode}")
    except Exception as e:
        print(f"关闭PotPlayer时遇到错误：{e}")

if __name__ == "__main__":
    config = configparser.ConfigParser()

    # 使用UTF-8编码打开配置文件
    with open('close_config.ini', 'r', encoding='utf-8') as configfile:
        config.read_file(configfile)

    # 获取程序列表（以分号分隔）
    programs_str = config['Params']['programs_str']
    programs = programs_str.split('/')

    # 根据配置调用关闭函数
    for program in programs:
        if program == "Honeyview":
            close_honeyview()
        elif program == "3dsmax":
            close_3ds_max()
        elif program == "docx":
            close_docx_force()
        elif program == "PotPlayer":
            close_potplayer()
        else:
            print(f"未定义关闭程序的方法: {program}")
