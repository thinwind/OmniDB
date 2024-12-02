#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
Copyright (c) 2020-2024, Yehua Shang

@Author: niceshang@outlook.com
@Created at: 2024-11-27 11:05:22

This module is used to compare the difference between two databases.
    
"""

import json


def read_db_file(file_path):
    # 读取 JSON 文件
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
        data["file_path"] = file_path

    return data


class DatabaseDiff:
    def __init__(self, db1, db2):
        self.db1_file = db1["file_path"]
        self.db2_file = db2["file_path"]
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

    # 比较两个 DDL
    @staticmethod
    def compare_ddl(ddl1, ddl2):
        if ddl1 == ddl2:
            return True
        ddl1 = ddl1.replace("\n", " ").replace("\t", " ").strip().lower()
        ddl2 = ddl2.replace("\n", " ").replace("\t", " ").strip().lower()
        return ddl1 == ddl2

    def compare(self):
        # 查找单边表
        self.find_single_side_table()
        # 比对共同表的差异
        self.compare_common_table()

        # 比较视图
        self.compare_views()

        # 比较存储过程
        self.compare_procedures()

    def compare_procedures(self):
        # 比较存储过程
        self.procedures_only_in_db1 = []
        self.procedures_only_in_db2 = []
        procedures1 = self.db1["procedures"]
        procedures2 = self.db2["procedures"]
        procedures1.sort(key=lambda x: x["name"].upper())
        procedures2.sort(key=lambda x: x["name"].upper())

        self.procedures_only_in_db1 = []
        self.procedures_only_in_db2 = []
        self.diff_procedures = []
        self.common_procedures = []

        cursor1 = 0
        cursor2 = 0
        while cursor1 < len(procedures1) and cursor2 < len(procedures2):
            procedure1 = procedures1[cursor1]
            procedure2 = procedures2[cursor2]
            if self.ease_compare(procedure1["name"], procedure2["name"]):
                # 同一存储过程
                if not self.ease_compare(
                    procedure1["definition"], procedure2["definition"]
                ):
                    self.diff_procedures.append(
                        {
                            "procedure_name": procedure1["name"],
                            "procedure1_def": procedure1["definition"],
                            "procedure2_def": procedure2["definition"],
                        }
                    )
                else:
                    self.common_procedures.append(procedure1["name"])
                cursor1 += 1
                cursor2 += 1
            elif procedure1["name"].upper() < procedure2["name"].upper():
                # 存储过程1有,存储过程2没有
                self.procedures_only_in_db1.append(procedure1["name"])
                cursor1 += 1
            else:
                # 存储过程2有,存储过程1没有
                self.procedures_only_in_db2.append(procedure2["name"])
                cursor2 += 1
        # 处理剩余的存储过程
        while cursor1 < len(procedures1):
            procedure1 = procedures1[cursor1]
            self.procedures_only_in_db1.append(procedure1["name"])
            cursor1 += 1

        while cursor2 < len(procedures2):
            procedure2 = procedures2[cursor2]
            self.procedures_only_in_db2.append(procedure2["name"])

    def compare_views(self):
        # 比较视图
        self.views_only_in_db1 = []
        self.views_only_in_db2 = []
        self.views_in_both_db = []
        views1 = self.db1["views"]
        views2 = self.db2["views"]
        views1.sort(key=lambda x: x["v_name"].upper())
        views2.sort(key=lambda x: x["v_name"].upper())

        self.views_only_in_db1 = []
        self.views_only_in_db2 = []
        self.diff_views = []
        self.common_views = []

        cursor1 = 0
        cursor2 = 0
        while cursor1 < len(views1) and cursor2 < len(views2):
            view1 = views1[cursor1]
            view2 = views2[cursor2]
            if self.ease_compare(view1["v_name"], view2["v_name"]):
                # 同一视图
                if not self.ease_compare(view1["ddl"], view2["ddl"]):
                    self.diff_views.append(
                        {
                            "view_name": view1["v_name"],
                            "view1_ddl": view1["ddl"],
                            "view2_ddl": view2["ddl"],
                        }
                    )
                else:
                    self.common_views.append(view1["v_name"])
                cursor1 += 1
                cursor2 += 1
            elif view1["v_name"].upper() < view2["v_name"].upper():
                # 视图1有,视图2没有
                self.views_only_in_db1.append(view1["v_name"])
                cursor1 += 1
            else:
                # 视图2有,视图1没有
                self.views_only_in_db2.append(view2["v_name"])
                cursor2 += 1
        # 处理剩余的视图
        while cursor1 < len(views1):
            view1 = views1[cursor1]
            self.views_only_in_db1.append(view1["v_name"])
            cursor1 += 1

        while cursor2 < len(views2):
            view2 = views2[cursor2]
            self.views_only_in_db2.append(view2["v_name"])
            cursor2 += 1

    # 比较共同表
    def compare_common_table(self):
        # 比较两个数据库的差异
        self.common_tables = []
        self.diff_tables = []
        if len(self.tables_in_both_db) == 0:
            return

        for table_name in self.tables_in_both_db:
            table1 = self.find_table_by_name(self.db1["tables"], table_name)
            table2 = self.find_table_by_name(self.db2["tables"], table_name)
            # 比较 DDL
            if self.compare_ddl(table1["ddl"], table2["ddl"]):
                self.common_tables.append(table_name)
                continue

            table_diff_info = {}
            table_diff_info["table_name"] = table_name

            # DDL不同,比较列信息
            table_diff_info["diff_columns"] = self.compare_coloumns(table1, table2)

            # 比较索引(包含了主键和唯一索引)
            table_diff_info["diff_indices"] = self.compare_indices(
                table1["indexes"], table2["indexes"]
            )

            # 比较外键
            table_diff_info["diff_foreign_keys"] = self.compare_foreign_keys(
                table1["fks"], table2["fks"]
            )

            if (
                len(table_diff_info["diff_columns"]) > 0
                or len(table_diff_info["diff_indices"]) > 0
                or len(table_diff_info["diff_foreign_keys"]) > 0
            ): 
                t_diff_info=[]
                if len(table_diff_info["diff_columns"]) > 0:
                    t_diff_info.append("Columns")
                if len(table_diff_info["diff_indices"]) > 0:
                    t_diff_info.append("Indices")
                if len(table_diff_info["diff_foreign_keys"]) > 0:
                    t_diff_info.append("Foreign Keys")
                
                table_diff_info["diff_type"] = "/".join(t_diff_info)
                self.diff_tables.append(table_diff_info)
            else:
                self.common_tables.append(table_name)

    def compare_foreign_keys(self, fks1, fks2):
        fks1.sort(key=lambda x: x["name"].upper())
        fks2.sort(key=lambda x: x["name"].upper())
        cursor1 = 0
        cursor2 = 0
        diff_fks = []
        while cursor1 < len(fks1) and cursor2 < len(fks2):
            fk1 = fks1[cursor1]
            fk2 = fks2[cursor2]
            if self.ease_compare(fk1["name"], fk2["name"]):
                # 同一外键
                fk1_def = self.build_foreign_key_signature(fk1)
                fk2_def = self.build_foreign_key_signature(fk2)

                if not self.ease_compare(fk1_def, fk2_def):
                    diff_fks.append(
                        {"fk_name": fk1["name"], "fk1_def": fk1_def, "fk2_def": fk2_def}
                    )

                # 一起下移
                cursor1 += 1
                cursor2 += 1
            elif fk1["name"].upper() < fk2["name"].upper():
                # 外键1有,外键2没有
                diff_fks.append(
                    {
                        "fk_name": fk1["name"],
                        "fk1_def": self.build_foreign_key_signature(fk1),
                        "fk2_def": "Not Exist",
                    }
                )
                cursor1 += 1
            else:
                # 外键2有,外键1没有
                diff_fks.append(
                    {
                        "fk_name": fk2["name"],
                        "fk1_def": "Not Exist",
                        "fk2_def": self.build_foreign_key_signature(fk2),
                    }
                )
                cursor2 += 1
        # 处理剩余的
        while cursor1 < len(fks1):
            fk1 = fks1[cursor1]
            diff_fks.append(
                {
                    "fk_name": fk1["name"],
                    "fk1_def": self.build_foreign_key_signature(fk1),
                    "fk2_def": "Not Exist",
                }
            )
            cursor1 += 1
        while cursor2 < len(fks2):
            fk2 = fks2[cursor2]
            diff_fks.append(
                {
                    "fk_name": fk2["name"],
                    "fk1_def": "Not Exist",
                    "fk2_def": self.build_foreign_key_signature(fk2),
                }
            )
            cursor2 += 1
        return diff_fks

    def build_foreign_key_signature(self, fk):
        fk1_cols = [
            item["column_name"] + "," + item["r_column_name"] for item in fk["columns"]
        ]
        fk1_def = (
            f"{fk['r_table_name']}:{fk['delete_rule']}:{fk['update_rule']}:"
            + ",".join(sorted(fk1_cols))
        )
        return fk1_def

    def compare_indices(self, indices1, indices2):
        indices1.sort(key=lambda x: x["name"].upper())
        indices2.sort(key=lambda x: x["name"].upper())
        cursor1 = 0
        cursor2 = 0
        diff_indices = []
        while cursor1 < len(indices1) and cursor2 < len(indices2):
            index1 = indices1[cursor1]
            index2 = indices2[cursor2]
            if self.ease_compare(index1["name"], index2["name"]):
                # 同一索引
                index1_def = self.build_index_signature(index1)
                index2_def = self.build_index_signature(index2)
                if not self.ease_compare(index1_def, index2_def):
                    diff_indices.append(
                        {
                            "index_name": index1["name"],
                            "index1_def": index1_def,
                            "index2_def": index2_def,
                        }
                    )

                # 一起下移
                cursor1 += 1
                cursor2 += 1
            elif index1["name"].upper() < index2["name"].upper():
                # 索引1有,索引2没有
                diff_indices.append(
                    {
                        "index_name": index1["name"],
                        "index1_def": self.build_index_signature(index1),
                        "index2_def": "Not Exist",
                    }
                )
                cursor1 += 1
            else:
                # 索引2有,索引1没有
                diff_indices.append(
                    {
                        "index_name": index2["name"],
                        "index1_def": "Not Exist",
                        "index2_def": self.build_index_signature(index2),
                    }
                )
                cursor2 += 1
        # 处理剩余的索引
        while cursor1 < len(indices1):
            index1 = indices1[cursor1]
            diff_indices.append(
                {
                    "index_name": index1["name"],
                    "index1_def": self.build_index_signature(index1),
                    "index2_def": "Not Exist",
                }
            )
            cursor1 += 1
        while cursor2 < len(indices2):
            index2 = indices2[cursor2]
            diff_indices.append(
                {
                    "index_name": index2["name"],
                    "index1_def": "Not Exist",
                    "index2_def": self.build_index_signature(index2),
                }
            )
            cursor2 += 1

        return diff_indices

    def build_index_signature(self, index1):
        return index1["uniqueness"] + ":" + ",".join(index1["columns"])

    def compare_coloumns(self, table1, table2):
        diff_columns = []
        # 比较列
        colums1 = table1["columns"]
        colums2 = table2["columns"]
        colums1.sort(key=lambda x: x["v_column_name"].upper())
        colums2.sort(key=lambda x: x["v_column_name"].upper())
        cursor1 = 0
        cursor2 = 0
        while cursor1 < len(colums1) and cursor2 < len(colums2):
            col1 = colums1[cursor1]
            col2 = colums2[cursor2]
            if self.ease_compare(col1["v_column_name"], col2["v_column_name"]):
                # 同一列
                col1_def = (
                    col1["v_data_type"]
                    + " "
                    + col1["v_data_length"]
                    + " "
                    + col1["v_nullable"]
                )
                col2_def = (
                    col2["v_data_type"]
                    + " "
                    + col2["v_data_length"]
                    + " "
                    + col2["v_nullable"]
                )
                if not self.ease_compare(col1_def, col2_def):
                    diff_columns.append(
                        {
                            "col_name": col1["v_column_name"],
                            "col1_def": col1_def,
                            "col2_def": col2_def,
                        }
                    )

                # 一起下移
                cursor1 += 1
                cursor2 += 1
            elif colums1[cursor1]["v_column_name"].upper() < colums2[cursor2]["v_column_name"].upper():
                # 表1有,表2没有
                diff_columns.append(
                    {
                        "col_name": col1["v_column_name"],
                        "col1_def": col1["v_data_type"]
                        + " "
                        + col1["v_data_length"]
                        + " "
                        + col1["v_nullable"],
                        "col2_def": "Not Exist",
                    }
                )
                cursor1 += 1
            else:
                # 表2有,表1没有
                diff_columns.append(
                    {
                        "col_name": col2["v_column_name"],
                        "col1_def": "Not Exist",
                        "col2_def": col2["v_data_type"]
                        + " "
                        + col2["v_data_length"]
                        + " "
                        + col2["v_nullable"],
                    }
                )
                cursor2 += 1
        # 处理剩余的列
        while cursor1 < len(colums1):
            col1 = colums1[cursor1]
            diff_columns.append(
                {
                    "col_name": col1["v_column_name"],
                    "col1_def": col1["v_data_type"]
                    + " "
                    + col1["v_data_length"]
                    + " "
                    + col1["v_nullable"],
                    "col2_def": "Not Exist",
                }
            )
            cursor1 += 1
        while cursor2 < len(colums2):
            col2 = colums2[cursor2]
            diff_columns.append(
                {
                    "col_name": col2["v_column_name"],
                    "col1_def": "Not Exist",
                    "col2_def": col2["v_data_type"]
                    + " "
                    + col2["v_data_length"]
                    + " "
                    + col2["v_nullable"],
                }
            )
            cursor2 += 1

        return diff_columns

    def find_table_by_name(self, tables, table_name):
        for table in tables:
            if self.ease_compare(table["v_name"], table_name):
                return table

        return None

    # 查找的单边表
    def find_single_side_table(self):
        # 比较两个数据库的差异
        tables1 = self.db1["tables"]
        tables2 = self.db2["tables"]

        db1_table_names = {table["v_name"].upper() for table in tables1}
        db2_table_names = {table["v_name"].upper() for table in tables2}

        self.tables_only_in_db1 = list(db1_table_names - db2_table_names)
        self.tables_only_in_db2 = list(db2_table_names - db1_table_names)
        self.tables_in_both_db = list(db1_table_names & db2_table_names)


if __name__ == '__main__':
    file_dir = '/home/sany/tmp/omnidb-files/'
    db1 = read_db_file(file_dir + "my_test_24-11-28-110158_00.json")
    db2 = read_db_file(file_dir + "my_test_24-11-28-112640_01.json")

    db_diff = DatabaseDiff(db1, db2)
    db_diff.compare()

    del db_diff.db1
    del db_diff.db2
    
    # db_diff.db2=None
    diff_file_path = file_dir + "my_test_1129_diff.json"
    with open(diff_file_path, "w", encoding="UTF-8") as f:
        f.write(json.dumps(db_diff,indent=4,default=lambda x: x.__dict__))
    
    print(f"diff result has been saved to {diff_file_path}")
