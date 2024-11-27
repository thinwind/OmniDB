#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
Copyright (c) 2020-2024, Yehua Shang
Author: niceshang@outlook.com
Created at 2024-11-27 11:05:22

This module is used to compare the difference between two databases.
    
"""

import json

from django import db


def read_db_file(file_path):
    # 读取 JSON 文件
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
        data["file_path"] = file_path

    return data


class DatabaseDiff:
    def __init__(self, db1, db2):
        self.db1 = db1
        self.db2 = db2

     # staticmethod 比较字符串,忽略大小写
    @staticmethod
    def ease_compare(str1, str2):
        if str1 == str2:
            return True
        if str1 is None and str2 is None:
            return True
        if str1 is None or str2 is None:
            return False
        return str1.lower() == str2.lower()

    def compare(self):
        # 查找单边表
        self.find_single_side_table()
        # 比对共同表的差异
        self.compare_common_table()

    # 比较共同表
    def compare_common_table(self):
        # 比较两个数据库的差异
        self.common_tabls = []
        self.diff_tables = []
        if len(self.tables_in_both_db) == 0:
            return

        for table_name in self.tables_in_both_db:
            table1 = self.find_table_by_name(self.db1["tables"], table_name)
            table2 = self.find_table_by_name(self.db2["tables"], table_name)
            table1_ddl = table1["ddl"].lower()
            table2_ddl = table2["ddl"].lower()
            if table1_ddl == table2_ddl:
                self.common_tabls.append(table_name)
                continue
            
            table_diff_info = None

            def init_table_diff_info():
                global table_diff_info
                if table_diff_info is None:
                    table_diff_info = {}
                    table_diff_info["table_name"] = table_name
                    table_diff_info["diff_columns"] = []
                    table_diff_info["diff_indices"] = []
                    table_diff_info["diff_foreign_keys"] = []
                    self.diff_tables.append(table_diff_info)

            # ddl不同,不代表表结构不同
            # 比较列
            colums1 = table1["columns"]
            colums2 = table2["columns"]
            colums1.sort(key = lambda x: x['v_column_name'])
            colums2.sort(key = lambda x: x['v_column_name'])
            cursor1 = 0
            cursor2 = 0
            while cursor1 < len(colums1) and cursor2 < len(colums2):
                col1 = colums1[cursor1]
                col2 = colums2[cursor2]
                if self.ease_compare(col1["v_column_name"], col2["v_column_name"]):
                    # 同一列
                    col1_def = col1['v_data_type'] + " " + col1['v_data_length'] + " " + col1['v_nullable']
                    col2_def = col2['v_data_type'] + " " + col2['v_data_length'] + " " + col2['v_nullable']
                    if not self.ease_compare(col1_def, col2_def):
                        init_table_diff_info()
                        table_diff_info["diff_columns"].append({
                            "col_name": col1["v_column_name"],
                            "col1_def": col1_def,
                            "col2_def": col2_def
                        })
                        
                    # 一起下移
                    cursor1 += 1
                    cursor2 += 1
                elif colums1[cursor1]["v_column_name"] < colums2[cursor2]["v_column_name"]:
                    # 表1有,表2没有
                    init_table_diff_info()
                    table_diff_info["diff_columns"].append({
                        "col_name": col1["v_column_name"],
                        "col1_def": col1['v_data_type'] + " " + col1['v_data_length'] + " " + col1['v_nullable'],
                        "col2_def": "Not Exist"
                    })
                    cursor1 += 1
                else:
                    # 表2有,表1没有
                    init_table_diff_info()
                    table_diff_info["diff_columns"].append({
                        "col_name": col2["v_column_name"],
                        "col1_def": "Not Exist",
                        "col2_def": col2['v_data_type'] + " " + col2['v_data_length'] + " " + col2['v_nullable']
                    })
                    cursor2 += 1
            # 处理剩余的列
            while cursor1 < len(colums1):
                col1 = colums1[cursor1]
                init_table_diff_info()
                table_diff_info["diff_columns"].append({
                    "col_name": col1["v_column_name"],
                    "col1_def": col1['v_data_type'] + " " + col1['v_data_length'] + " " + col1['v_nullable'],
                    "col2_def": "Not Exist"
                })
                cursor1 += 1
            while cursor2 < len(colums2):
                col2 = colums2[cursor2]
                init_table_diff_info()
                table_diff_info["diff_columns"].append({
                    "col_name": col2["v_column_name"],
                    "col1_def": "Not Exist",
                    "col2_def": col2['v_data_type'] + " " + col2['v_data_length'] + " " + col2['v_nullable']
                })
                cursor2 += 1


            # 比较索引(包含了主键和唯一索引)

            # 比较外键

   
    def find_table_by_name(self, tables, table_name):
        for table in tables:
            if table["v_name"].lower() == table_name.lower():
                return table

        return None

    # 查找的单边表
    def find_single_side_table(self, tables1, tables2):
        # 比较两个数据库的差异
        tables1 = self.db1["tables"]
        tables2 = self.db2["tables"]

        db1_table_names = {table["v_name"] for table in tables1}
        db2_table_names = {table["v_name"] for table in tables2}

        self.tables_only_in_db1 = list(db1_table_names - db2_table_names)
        self.tables_only_in_db2 = list(db2_table_names - db1_table_names)
        self.tables_in_both_db = list(db1_table_names & db2_table_names)

    def compare_table(self, table1, table2):
        # 比较两个表的差异
        diff = []
        for field in table1:
            if field not in table2:
                diff.append({"field": field, "diff": "field not exist"})
            else:
                diff.append(
                    {
                        "field": field,
                        "diff": self.compare_field(table1[field], table2[field]),
                    }
                )

        return diff

    def compare_field(self, field1, field2):
        # 比较两个字段的差异
        diff = {}
        for key in field1:
            if key not in field2:
                diff[key] = "field not exist"
            elif field1[key] != field2[key]:
                diff[key] = "field value not equal"

        return diff
