# -*- coding: utf-8 -*-
"""
@Time   :  2024-11 月-22 10:40
@Author :  Shang Yehua
@Email  :  niceshang@outlook.com
@Desc   :  
        文件工具
"""
from datetime import datetime

name_seq = 0


def save_txt_file(path, name, ext, content, add_postfix=True):
    global name_seq
    if add_postfix:
        name = (
            name
            + "_"
            + datetime.now().strftime("%y-%m-%d-%H%M%S")
            + "_"
            + f"{(name_seq%100):02d}"
        )
        name_seq += 1
    file_path = path + name + "." + ext
    with open(file_path, "w", encoding="UTF-8") as f:
        f.write(content)
    return file_path


def append_txt_file(file_path, content):
    with open(file_path, "a", encoding="UTF-8") as f:
        f.write("\n")
        f.write(content)
    return file_path
