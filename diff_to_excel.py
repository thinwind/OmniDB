#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
Copyright (c) 2024, Yehua Shang

  @Author: Yehua Shang
  @Email:  niceshang@outlook.com
  @Time:   2024-11-29 17:11:33

    将数据库差异信息导出到excel文件

'''

from openpyxl import Workbook,load_workbook,cell

# 将数据量先写入到sheet中
def write_table_count(sheet,db_info):
    