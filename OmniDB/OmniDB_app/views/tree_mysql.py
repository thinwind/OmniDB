import json


from django.http import JsonResponse
from OmniDB_app.utils import file_util
from OmniDB_app.views.memory_objects import user_authenticated, database_required

from OmniDB.custom_settings import DB_INFO_FILE_DIR


@user_authenticated
@database_required(p_check_timeout=True, p_open_connection=True)
def get_tree_info(request, v_database):

    v_return = {}
    v_return["v_data"] = ""
    v_return["v_error"] = False
    v_return["v_error_id"] = -1

    # json_object = json.loads(request.POST.get("data", None))
    # v_database_index = json_object["p_database_index"]
    # v_tab_id = json_object["p_tab_id"]

    try:
        v_return["v_data"] = {
            "v_mode": "database",
            "v_database_return": {
                "v_database": v_database.GetName(),
                "version": v_database.GetVersion(),
                "v_username": v_database.GetUserName(),
                "superuser": v_database.GetUserSuper(),
                "create_role": v_database.TemplateCreateRole().v_text,
                "alter_role": v_database.TemplateAlterRole().v_text,
                "drop_role": v_database.TemplateDropRole().v_text,
                #'create_tablespace': v_database.TemplateCreateTablespace().v_text,
                #'alter_tablespace': v_database.TemplateAlterTablespace().v_text,
                #'drop_tablespace': v_database.TemplateDropTablespace().v_text,
                "create_database": v_database.TemplateCreateDatabase().v_text,
                "alter_database": v_database.TemplateAlterDatabase().v_text,
                "drop_database": v_database.TemplateDropDatabase().v_text,
                #'create_sequence': v_database.TemplateCreateSequence().v_text,
                #'alter_sequence': v_database.TemplateAlterSequence().v_text,
                #'drop_sequence': v_database.TemplateDropSequence().v_text,
                "create_function": v_database.TemplateCreateFunction().v_text,
                "drop_function": v_database.TemplateDropFunction().v_text,
                "create_procedure": v_database.TemplateCreateProcedure().v_text,
                "drop_procedure": v_database.TemplateDropProcedure().v_text,
                #'create_triggerfunction': v_database.TemplateCreateTriggerFunction().v_text,
                #'drop_triggerfunction': v_database.TemplateDropTriggerFunction().v_text,
                "create_view": v_database.TemplateCreateView().v_text,
                "drop_view": v_database.TemplateDropView().v_text,
                "create_table": v_database.TemplateCreateTable().v_text,
                "alter_table": v_database.TemplateAlterTable().v_text,
                "drop_table": v_database.TemplateDropTable().v_text,
                "create_column": v_database.TemplateCreateColumn().v_text,
                "alter_column": v_database.TemplateAlterColumn().v_text,
                "drop_column": v_database.TemplateDropColumn().v_text,
                "create_primarykey": v_database.TemplateCreatePrimaryKey().v_text,
                "drop_primarykey": v_database.TemplateDropPrimaryKey().v_text,
                "create_unique": v_database.TemplateCreateUnique().v_text,
                "drop_unique": v_database.TemplateDropUnique().v_text,
                "create_foreignkey": v_database.TemplateCreateForeignKey().v_text,
                "drop_foreignkey": v_database.TemplateDropForeignKey().v_text,
                "create_index": v_database.TemplateCreateIndex().v_text,
                "drop_index": v_database.TemplateDropIndex().v_text,
                #'create_trigger': v_database.TemplateCreateTrigger().v_text,
                #'create_view_trigger': v_database.TemplateCreateViewTrigger().v_text,
                #'alter_trigger': v_database.TemplateAlterTrigger().v_text,
                #'enable_trigger': v_database.TemplateEnableTrigger().v_text,
                #'disable_trigger': v_database.TemplateDisableTrigger().v_text,
                #'drop_trigger': v_database.TemplateDropTrigger().v_text,
                #'create_partition': v_database.TemplateCreatePartition().v_text,
                #'noinherit_partition': v_database.TemplateNoInheritPartition().v_text,
                #'drop_partition': v_database.TemplateDropPartition().v_text
                "delete": v_database.TemplateDelete().v_text,
            },
        }
    except Exception as exc:
        v_return["v_data"] = {"password_timeout": True, "message": str(exc)}
        v_return["v_error"] = True
        return JsonResponse(v_return)

    return JsonResponse(v_return)


@user_authenticated
@database_required(p_check_timeout=True, p_open_connection=True)
def get_properties(request, v_database):

    v_return = {}
    v_return["v_data"] = ""
    v_return["v_error"] = False
    v_return["v_error_id"] = -1

    json_object = json.loads(request.POST.get("data", None))
    # v_database_index = json_object["p_database_index"]
    v_data = json_object["p_data"]
    # v_tab_id = json_object["p_tab_id"]

    v_list_properties = []
    v_ddl = ""

    try:
        v_properties = v_database.GetProperties(
            v_data["p_schema"], v_data["p_table"], v_data["p_object"], v_data["p_type"]
        )
        for v_property in v_properties.Rows:
            v_list_properties.append([v_property["Property"], v_property["Value"]])
        v_ddl = v_database.GetDDL(
            v_data["p_schema"], v_data["p_table"], v_data["p_object"], v_data["p_type"]
        )
    except Exception as exc:
        v_return["v_data"] = {"password_timeout": True, "message": str(exc)}
        v_return["v_error"] = True
        return JsonResponse(v_return)

    v_return["v_data"] = {"properties": v_list_properties, "ddl": v_ddl}

    return JsonResponse(v_return)


@user_authenticated
@database_required(p_check_timeout=True, p_open_connection=True)
def get_tables(request, v_database):
    v_return = {}
    v_return["v_data"] = ""
    v_return["v_error"] = False
    v_return["v_error_id"] = -1

    json_object = json.loads(request.POST.get("data", None))
    v_schema = json_object["p_schema"]

    v_list_tables = []
    try:
        v_list_tables = get_tables_data(v_database, v_schema)
    except Exception as exc:
        v_return["v_data"] = {"password_timeout": True, "message": str(exc)}
        v_return["v_error"] = True
        return JsonResponse(v_return)

    v_return["v_data"] = v_list_tables
    return JsonResponse(v_return)


def get_tables_data(v_database, v_schema):
    v_list_tables = []
    v_tables = v_database.QueryTables(False, v_schema)
    for v_table in v_tables.Rows:
        v_table_data = {
            "v_name": v_table["table_name"],
            "v_has_primary_keys": v_database.v_has_primary_keys,
            "v_has_foreign_keys": v_database.v_has_foreign_keys,
            "v_has_uniques": v_database.v_has_uniques,
            "v_has_indexes": v_database.v_has_indexes,
            "v_has_checks": v_database.v_has_checks,
            "v_has_excludes": v_database.v_has_excludes,
            "v_has_rules": v_database.v_has_rules,
            "v_has_triggers": v_database.v_has_triggers,
            "v_has_partitions": v_database.v_has_partitions,
            "v_has_statistics": v_database.v_has_statistics,
        }
        v_list_tables.append(v_table_data)

    return v_list_tables


@user_authenticated
@database_required(p_check_timeout=True, p_open_connection=True)
def get_columns(request, v_database):

    v_return = {}
    v_return["v_data"] = ""
    v_return["v_error"] = False
    v_return["v_error_id"] = -1

    json_object = json.loads(request.POST.get("data", None))
    # v_database_index = json_object["p_database_index"]
    v_table = json_object["p_table"]
    v_schema = json_object["p_schema"]
    # v_tab_id = json_object["p_tab_id"]

    v_list_columns = []

    try:
        v_columns = v_database.QueryTablesFields(v_table, False, v_schema)
        for v_column in v_columns.Rows:
            v_column_data = {
                "v_column_name": v_column["column_name"],
                "v_data_type": v_column["data_type"],
                "v_data_length": v_column["data_length"],
                "v_nullable": v_column["nullable"],
            }
            v_list_columns.append(v_column_data)
    except Exception as exc:
        v_return["v_data"] = {"password_timeout": True, "message": str(exc)}
        v_return["v_error"] = True
        return JsonResponse(v_return)

    v_return["v_data"] = v_list_columns

    return JsonResponse(v_return)

def get_columns_data(v_database, v_table, v_schema):
    v_list_columns = []
    v_columns = v_database.QueryTablesFields(v_table, False, v_schema)
    for v_column in v_columns.Rows:
        v_column_data = {
            "v_column_name": v_column["column_name"],
            "v_data_type": v_column["data_type"],
            "v_data_length": v_column["data_length"],
            "v_nullable": v_column["nullable"],
        }
        v_list_columns.append(v_column_data)
    return v_list_columns


@user_authenticated
@database_required(p_check_timeout=True, p_open_connection=True)
def get_pk(request, v_database):

    v_return = {}
    v_return["v_data"] = ""
    v_return["v_error"] = False
    v_return["v_error_id"] = -1

    json_object = json.loads(request.POST.get("data", None))
    # v_database_index = json_object["p_database_index"]
    v_table = json_object["p_table"]
    v_schema = json_object["p_schema"]
    # v_tab_id = json_object["p_tab_id"]

    v_list_pk = []

    try:
        v_pks = v_database.QueryTablesPrimaryKeys(v_table, False, v_schema)
        for v_pk in v_pks.Rows:
            v_pk_data = []
            v_pk_data.append(v_pk["constraint_name"])
            v_list_pk.append(v_pk_data)
    except Exception as exc:
        v_return["v_data"] = {"password_timeout": True, "message": str(exc)}
        v_return["v_error"] = True
        return JsonResponse(v_return)

    v_return["v_data"] = v_list_pk

    return JsonResponse(v_return)


@user_authenticated
@database_required(p_check_timeout=True, p_open_connection=True)
def get_pk_columns(request, v_database):

    v_return = {}
    v_return["v_data"] = ""
    v_return["v_error"] = False
    v_return["v_error_id"] = -1

    json_object = json.loads(request.POST.get("data", None))
    # v_database_index = json_object["p_database_index"]
    v_pkey = json_object["p_key"]
    v_table = json_object["p_table"]
    v_schema = json_object["p_schema"]
    # v_tab_id = json_object["p_tab_id"]

    v_list_pk = []

    try:
        v_pks = v_database.QueryTablesPrimaryKeysColumns(
            v_pkey, v_table, False, v_schema
        )
        for v_pk in v_pks.Rows:
            v_pk_data = []
            v_pk_data.append(v_pk["column_name"])
            v_list_pk.append(v_pk_data)
    except Exception as exc:
        v_return["v_data"] = {"password_timeout": True, "message": str(exc)}
        v_return["v_error"] = True
        return JsonResponse(v_return)

    v_return["v_data"] = v_list_pk

    return JsonResponse(v_return)


@user_authenticated
@database_required(p_check_timeout=True, p_open_connection=True)
def get_fks(request, v_database):

    v_return = {}
    v_return["v_data"] = ""
    v_return["v_error"] = False
    v_return["v_error_id"] = -1

    json_object = json.loads(request.POST.get("data", None))
    # v_database_index = json_object["p_database_index"]
    v_table = json_object["p_table"]
    v_schema = json_object["p_schema"]
    # v_tab_id = json_object["p_tab_id"]

    v_list_fk = []

    try:
        v_fks = v_database.QueryTablesForeignKeys(v_table, False, v_schema)
        for v_fk in v_fks.Rows:
            v_fk_data = []
            v_fk_data.append(v_fk["constraint_name"])
            v_fk_data.append(v_fk["r_table_name"])
            v_fk_data.append(v_fk["delete_rule"])
            v_fk_data.append(v_fk["update_rule"])
            v_list_fk.append(v_fk_data)
    except Exception as exc:
        v_return["v_data"] = {"password_timeout": True, "message": str(exc)}
        v_return["v_error"] = True
        return JsonResponse(v_return)

    v_return["v_data"] = v_list_fk

    return JsonResponse(v_return)


@user_authenticated
@database_required(p_check_timeout=True, p_open_connection=True)
def get_fks_columns(request, v_database):

    v_return = {}
    v_return["v_data"] = ""
    v_return["v_error"] = False
    v_return["v_error_id"] = -1

    json_object = json.loads(request.POST.get("data", None))
    # v_database_index = json_object["p_database_index"]
    v_fkey = json_object["p_fkey"]
    v_table = json_object["p_table"]
    v_schema = json_object["p_schema"]
    # v_tab_id = json_object["p_tab_id"]

    v_list_fk = []

    try:
        v_fks = v_database.QueryTablesForeignKeysColumns(
            v_fkey, v_table, False, v_schema
        )
        for v_fk in v_fks.Rows:
            v_fk_data = []
            v_fk_data.append(v_fk["r_table_name"])
            v_fk_data.append(v_fk["delete_rule"])
            v_fk_data.append(v_fk["update_rule"])
            v_fk_data.append(v_fk["column_name"])
            v_fk_data.append(v_fk["r_column_name"])
            v_list_fk.append(v_fk_data)
    except Exception as exc:
        v_return["v_data"] = {"password_timeout": True, "message": str(exc)}
        v_return["v_error"] = True
        return JsonResponse(v_return)

    v_return["v_data"] = v_list_fk

    return JsonResponse(v_return)


@user_authenticated
@database_required(p_check_timeout=True, p_open_connection=True)
def get_uniques(request, v_database):

    v_return = {}
    v_return["v_data"] = ""
    v_return["v_error"] = False
    v_return["v_error_id"] = -1

    json_object = json.loads(request.POST.get("data", None))
    # v_database_index = json_object["p_database_index"]
    v_table = json_object["p_table"]
    v_schema = json_object["p_schema"]
    # v_tab_id = json_object["p_tab_id"]

    v_list_uniques = []

    try:
        v_uniques = v_database.QueryTablesUniques(v_table, False, v_schema)
        for v_unique in v_uniques.Rows:
            v_unique_data = []
            v_unique_data.append(v_unique["constraint_name"])
            v_list_uniques.append(v_unique_data)
    except Exception as exc:
        v_return["v_data"] = {"password_timeout": True, "message": str(exc)}
        v_return["v_error"] = True
        return JsonResponse(v_return)

    v_return["v_data"] = v_list_uniques

    return JsonResponse(v_return)


@user_authenticated
@database_required(p_check_timeout=True, p_open_connection=True)
def get_uniques_columns(request, v_database):

    v_return = {}
    v_return["v_data"] = ""
    v_return["v_error"] = False
    v_return["v_error_id"] = -1

    json_object = json.loads(request.POST.get("data", None))
    # v_database_index = json_object["p_database_index"]
    v_unique = json_object["p_unique"]
    v_table = json_object["p_table"]
    v_schema = json_object["p_schema"]
    # v_tab_id = json_object["p_tab_id"]

    v_list_uniques = []

    try:
        v_uniques = v_database.QueryTablesUniquesColumns(
            v_unique, v_table, False, v_schema
        )
        for v_unique in v_uniques.Rows:
            v_unique_data = []
            v_unique_data.append(v_unique["column_name"])
            v_list_uniques.append(v_unique_data)
    except Exception as exc:
        v_return["v_data"] = {"password_timeout": True, "message": str(exc)}
        v_return["v_error"] = True
        return JsonResponse(v_return)

    v_return["v_data"] = v_list_uniques

    return JsonResponse(v_return)


@user_authenticated
@database_required(p_check_timeout=True, p_open_connection=True)
def get_indexes(request, v_database):

    v_return = {}
    v_return["v_data"] = ""
    v_return["v_error"] = False
    v_return["v_error_id"] = -1

    json_object = json.loads(request.POST.get("data", None))
    # v_database_index = json_object["p_database_index"]
    v_table = json_object["p_table"]
    v_schema = json_object["p_schema"]
    # v_tab_id = json_object["p_tab_id"]

    v_list_indexes = []

    try:
        v_indexes = v_database.QueryTablesIndexes(v_table, False, v_schema)
        for v_index in v_indexes.Rows:
            v_index_data = []
            v_index_data.append(v_index["index_name"])
            v_index_data.append(v_index["uniqueness"])
            v_list_indexes.append(v_index_data)
    except Exception as exc:
        v_return["v_data"] = {"password_timeout": True, "message": str(exc)}
        v_return["v_error"] = True
        return JsonResponse(v_return)

    v_return["v_data"] = v_list_indexes

    return JsonResponse(v_return)


@user_authenticated
@database_required(p_check_timeout=True, p_open_connection=True)
def get_indexes_columns(request, v_database):

    v_return = {}
    v_return["v_data"] = ""
    v_return["v_error"] = False
    v_return["v_error_id"] = -1

    json_object = json.loads(request.POST.get("data", None))
    # v_database_index = json_object["p_database_index"]
    v_index = json_object["p_index"]
    v_table = json_object["p_table"]
    v_schema = json_object["p_schema"]
    # v_tab_id = json_object["p_tab_id"]

    v_list_indexes = []

    try:
        v_indexes = v_database.QueryTablesIndexesColumns(
            v_index, v_table, False, v_schema
        )
        for v_index in v_indexes.Rows:
            v_index_data = []
            v_index_data.append(v_index["column_name"])
            v_list_indexes.append(v_index_data)
    except Exception as exc:
        v_return["v_data"] = {"password_timeout": True, "message": str(exc)}
        v_return["v_error"] = True
        return JsonResponse(v_return)

    v_return["v_data"] = v_list_indexes

    return JsonResponse(v_return)


@user_authenticated
@database_required(p_check_timeout=True, p_open_connection=True)
def get_databases(request, v_database):

    v_return = {}
    v_return["v_data"] = ""
    v_return["v_error"] = False
    v_return["v_error_id"] = -1

    # json_object = json.loads(request.POST.get("data", None))
    # v_database_index = json_object["p_database_index"]
    # v_tab_id = json_object["p_tab_id"]

    v_list_databases = []

    try:
        v_databases = v_database.QueryDatabases()
        for v_database in v_databases.Rows:
            v_database_data = {"v_name": v_database[0]}
            v_list_databases.append(v_database_data)
    except Exception as exc:
        v_return["v_data"] = {"password_timeout": True, "message": str(exc)}
        v_return["v_error"] = True
        return JsonResponse(v_return)

    v_return["v_data"] = v_list_databases

    return JsonResponse(v_return)


@user_authenticated
@database_required(p_check_timeout=True, p_open_connection=True)
def get_roles(request, v_database):

    v_return = {}
    v_return["v_data"] = ""
    v_return["v_error"] = False
    v_return["v_error_id"] = -1

    # json_object = json.loads(request.POST.get("data", None))
    # v_database_index = json_object["p_database_index"]
    # v_tab_id = json_object["p_tab_id"]

    v_list_roles = []

    try:
        v_roles = v_database.QueryRoles()
        for v_role in v_roles.Rows:
            v_role_data = {"v_name": v_role["role_name"]}
            v_list_roles.append(v_role_data)
    except Exception as exc:
        v_return["v_data"] = {"password_timeout": True, "message": str(exc)}
        v_return["v_error"] = True
        return JsonResponse(v_return)

    v_return["v_data"] = v_list_roles

    return JsonResponse(v_return)


@user_authenticated
@database_required(p_check_timeout=True, p_open_connection=True)
def get_functions(request, v_database):

    v_return = {}
    v_return["v_data"] = ""
    v_return["v_error"] = False
    v_return["v_error_id"] = -1

    json_object = json.loads(request.POST.get("data", None))
    # v_database_index = json_object["p_database_index"]
    v_schema = json_object["p_schema"]
    # v_tab_id = json_object["p_tab_id"]

    v_list_functions = []

    try:
        v_functions = v_database.QueryFunctions(False, v_schema)
        for v_function in v_functions.Rows:
            v_function_data = {"v_name": v_function["name"], "v_id": v_function["id"]}
            v_list_functions.append(v_function_data)
    except Exception as exc:
        v_return["v_data"] = {"password_timeout": True, "message": str(exc)}
        v_return["v_error"] = True
        return JsonResponse(v_return)

    v_return["v_data"] = v_list_functions

    return JsonResponse(v_return)


@user_authenticated
@database_required(p_check_timeout=True, p_open_connection=True)
def get_function_fields(request, v_database):

    v_return = {}
    v_return["v_data"] = ""
    v_return["v_error"] = False
    v_return["v_error_id"] = -1

    json_object = json.loads(request.POST.get("data", None))
    # v_database_index = json_object["p_database_index"]
    v_function = json_object["p_function"]
    v_schema = json_object["p_schema"]
    # v_tab_id = json_object["p_tab_id"]

    v_list_fields = []

    try:
        v_fields = v_database.QueryFunctionFields(v_function, v_schema)
        for v_field in v_fields.Rows:
            v_field_data = {"v_name": v_field["name"], "v_type": v_field["type"]}
            v_list_fields.append(v_field_data)
    except Exception as exc:
        v_return["v_data"] = {"password_timeout": True, "message": str(exc)}
        v_return["v_error"] = True
        return JsonResponse(v_return)

    v_return["v_data"] = v_list_fields

    return JsonResponse(v_return)


@user_authenticated
@database_required(p_check_timeout=True, p_open_connection=True)
def get_function_definition(request, v_database):

    v_return = {}
    v_return["v_data"] = ""
    v_return["v_error"] = False
    v_return["v_error_id"] = -1

    json_object = json.loads(request.POST.get("data", None))
    # v_database_index = json_object["p_database_index"]
    v_function = json_object["p_function"]
    # v_tab_id = json_object["p_tab_id"]

    try:
        v_return["v_data"] = v_database.GetFunctionDefinition(v_function)
    except Exception as exc:
        v_return["v_data"] = {"password_timeout": True, "message": str(exc)}
        v_return["v_error"] = True
        return JsonResponse(v_return)

    return JsonResponse(v_return)


@user_authenticated
@database_required(p_check_timeout=True, p_open_connection=True)
def get_procedures(request, v_database):

    v_return = {}
    v_return["v_data"] = ""
    v_return["v_error"] = False
    v_return["v_error_id"] = -1

    json_object = json.loads(request.POST.get("data", None))
    # v_database_index = json_object["p_database_index"]
    v_schema = json_object["p_schema"]
    # v_tab_id = json_object["p_tab_id"]

    v_list_functions = []

    try:
        v_functions = v_database.QueryProcedures(False, v_schema)
        for v_function in v_functions.Rows:
            v_function_data = {"v_name": v_function["name"], "v_id": v_function["id"]}
            v_list_functions.append(v_function_data)
    except Exception as exc:
        v_return["v_data"] = {"password_timeout": True, "message": str(exc)}
        v_return["v_error"] = True
        return JsonResponse(v_return)

    v_return["v_data"] = v_list_functions

    return JsonResponse(v_return)


@user_authenticated
@database_required(p_check_timeout=True, p_open_connection=True)
def get_procedure_fields(request, v_database):

    v_return = {}
    v_return["v_data"] = ""
    v_return["v_error"] = False
    v_return["v_error_id"] = -1

    json_object = json.loads(request.POST.get("data", None))
    # v_database_index = json_object["p_database_index"]
    v_function = json_object["p_procedure"]
    v_schema = json_object["p_schema"]
    # v_tab_id = json_object["p_tab_id"]

    v_list_fields = []

    try:
        v_fields = v_database.QueryProcedureFields(v_function, v_schema)
        for v_field in v_fields.Rows:
            v_field_data = {"v_name": v_field["name"], "v_type": v_field["type"]}
            v_list_fields.append(v_field_data)
    except Exception as exc:
        v_return["v_data"] = {"password_timeout": True, "message": str(exc)}
        v_return["v_error"] = True
        return JsonResponse(v_return)

    v_return["v_data"] = v_list_fields

    return JsonResponse(v_return)


@user_authenticated
@database_required(p_check_timeout=True, p_open_connection=True)
def get_procedure_definition(request, v_database):

    v_return = {}
    v_return["v_data"] = ""
    v_return["v_error"] = False
    v_return["v_error_id"] = -1

    json_object = json.loads(request.POST.get("data", None))
    # v_database_index = json_object["p_database_index"]
    v_function = json_object["p_procedure"]
    # v_tab_id = json_object["p_tab_id"]

    try:
        v_return["v_data"] = v_database.GetProcedureDefinition(v_function)
    except Exception as exc:
        v_return["v_data"] = {"password_timeout": True, "message": str(exc)}
        v_return["v_error"] = True
        return JsonResponse(v_return)

    return JsonResponse(v_return)


@user_authenticated
@database_required(p_check_timeout=True, p_open_connection=True)
def get_views(request, v_database):

    v_return = {}
    v_return["v_data"] = ""
    v_return["v_error"] = False
    v_return["v_error_id"] = -1

    json_object = json.loads(request.POST.get("data", None))
    v_schema = json_object["p_schema"]

    v_list_tables = []

    try:
        v_list_tables = get_view_data(v_database, v_schema)
    except Exception as exc:
        v_return["v_data"] = {"password_timeout": True, "message": str(exc)}
        v_return["v_error"] = True
        return JsonResponse(v_return)

    v_return["v_data"] = v_list_tables

    return JsonResponse(v_return)


def get_view_data(v_database, v_schema):
    v_list_views = []
    v_views = v_database.QueryViews(False, v_schema)
    for v_table in v_views.Rows:
        v_table_data = {
            "v_name": v_table["table_name"],
            "v_has_triggers": v_database.v_has_triggers,
        }
        v_list_views.append(v_table_data)
    return v_list_views


@user_authenticated
@database_required(p_check_timeout=True, p_open_connection=True)
def get_views_columns(request, v_database):

    v_return = {}
    v_return["v_data"] = ""
    v_return["v_error"] = False
    v_return["v_error_id"] = -1

    json_object = json.loads(request.POST.get("data", None))
    # v_database_index = json_object["p_database_index"]
    v_table = json_object["p_table"]
    v_schema = json_object["p_schema"]
    # v_tab_id = json_object["p_tab_id"]

    v_list_columns = []

    try:
        v_columns = v_database.QueryViewFields(v_table, False, v_schema)
        for v_column in v_columns.Rows:
            v_column_data = {
                "v_column_name": v_column["column_name"],
                "v_data_type": v_column["data_type"],
                "v_data_length": v_column["data_length"],
            }
            v_list_columns.append(v_column_data)
    except Exception as exc:
        v_return["v_data"] = {"password_timeout": True, "message": str(exc)}
        v_return["v_error"] = True
        return JsonResponse(v_return)

    v_return["v_data"] = v_list_columns

    return JsonResponse(v_return)


@user_authenticated
@database_required(p_check_timeout=True, p_open_connection=True)
def get_view_definition(request, v_database):

    v_return = {}
    v_return["v_data"] = ""
    v_return["v_error"] = False
    v_return["v_error_id"] = -1

    json_object = json.loads(request.POST.get("data", None))
    # v_database_index = json_object["p_database_index"]
    v_view = json_object["p_view"]
    v_schema = json_object["p_schema"]
    # v_tab_id = json_object["p_tab_id"]

    try:
        v_return["v_data"] = v_database.GetViewDefinition(v_view, v_schema)
    except Exception as exc:
        v_return["v_data"] = {"password_timeout": True, "message": str(exc)}
        v_return["v_error"] = True
        return JsonResponse(v_return)

    return JsonResponse(v_return)


@user_authenticated
@database_required(p_check_timeout=True, p_open_connection=True)
def kill_backend(request, v_database):

    v_return = {}
    v_return["v_data"] = ""
    v_return["v_error"] = False
    v_return["v_error_id"] = -1

    json_object = json.loads(request.POST.get("data", None))
    # v_database_index = json_object["p_database_index"]
    v_pid = json_object["p_pid"]
    # v_tab_id = json_object["p_tab_id"]

    try:
        v_data = v_database.Terminate(v_pid)
        v_return["v_data"] = v_data
    except Exception as exc:
        v_return["v_data"] = {"password_timeout": True, "message": str(exc)}
        v_return["v_error"] = True
        return JsonResponse(v_return)

    return JsonResponse(v_return)


@user_authenticated
@database_required(p_check_timeout=True, p_open_connection=True)
def template_select(request, v_database):

    v_return = {}
    v_return["v_data"] = ""
    v_return["v_error"] = False
    v_return["v_error_id"] = -1

    json_object = json.loads(request.POST.get("data", None))
    # v_database_index = json_object["p_database_index"]
    # v_tab_id = json_object["p_tab_id"]
    v_table = json_object["p_table"]
    v_schema = json_object["p_schema"]

    try:
        v_template = v_database.TemplateSelect(v_schema, v_table).v_text
    except Exception as exc:
        v_return["v_data"] = {"password_timeout": True, "message": str(exc)}
        v_return["v_error"] = True
        return JsonResponse(v_return)

    v_return["v_data"] = {"v_template": v_template}

    return JsonResponse(v_return)


@user_authenticated
@database_required(p_check_timeout=True, p_open_connection=True)
def template_insert(request, v_database):

    v_return = {}
    v_return["v_data"] = ""
    v_return["v_error"] = False
    v_return["v_error_id"] = -1

    json_object = json.loads(request.POST.get("data", None))
    # v_database_index = json_object["p_database_index"]
    # v_tab_id = json_object["p_tab_id"]
    v_table = json_object["p_table"]
    v_schema = json_object["p_schema"]

    try:
        v_template = v_database.TemplateInsert(v_schema, v_table).v_text
    except Exception as exc:
        v_return["v_data"] = {"password_timeout": True, "message": str(exc)}
        v_return["v_error"] = True
        return JsonResponse(v_return)

    v_return["v_data"] = {"v_template": v_template}

    return JsonResponse(v_return)


@user_authenticated
@database_required(p_check_timeout=True, p_open_connection=True)
def template_update(request, v_database):

    v_return = {}
    v_return["v_data"] = ""
    v_return["v_error"] = False
    v_return["v_error_id"] = -1

    json_object = json.loads(request.POST.get("data", None))
    # v_database_index = json_object["p_database_index"]
    # v_tab_id = json_object["p_tab_id"]
    v_table = json_object["p_table"]
    v_schema = json_object["p_schema"]

    try:
        v_template = v_database.TemplateUpdate(v_schema, v_table).v_text
    except Exception as exc:
        v_return["v_data"] = {"password_timeout": True, "message": str(exc)}
        v_return["v_error"] = True
        return JsonResponse(v_return)

    v_return["v_data"] = {"v_template": v_template}

    return JsonResponse(v_return)


@user_authenticated
@database_required(p_check_timeout=True, p_open_connection=True)
def save_info(request, v_database):
    v_return = {}
    v_return["v_data"] = "OK"
    v_return["v_error"] = False
    v_return["v_error_id"] = -1

    json_object = json.loads(request.POST.get("data", None))
    v_schema = json_object["p_schema"]

    db_info = {}

    # 查询表信息
    table_list = get_tables_data(v_database, v_schema)
    db_info["tables"] = table_list

    # 查询view信息并保存
    view_list = get_view_data(v_database, v_schema)
    db_info["views"] = view_list

    # 查询列信息
    for table in table_list:
        columns = get_columns_data(v_database, table["v_name"], v_schema)
        table["columns"] = columns
    
    # 查询view ddl
    for view in view_list:
        view["ddl"] = v_database.GetViewDefinition(view["v_name"], v_schema)
    
    # 查询table ddl
    for table in table_list:
        table["ddl"] = v_database.GetDDL(
            v_schema, table["v_name"], table["v_name"], 'table'
        )
        
    # 查询表数据量
    for table in table_list:
        table["count"] = v_database.ExecuteScalar(f"SELECT COUNT(*) FROM {table['v_name']}")

    # 查询主键信息
    for table in table_list:
        list_pk =[]
        pks = v_database.QueryTablesPrimaryKeys(table["v_name"], False, v_schema)
        for v_pk in pks.Rows:
            pk_data = {}
            pk_data["name"] = v_pk["constraint_name"]
            pk_columns = []
            pk_data["columns"] = pk_columns
            list_pk.append(pk_data)

            # 查询主键列信息
            v_pk_columns = v_database.QueryTablesPrimaryKeysColumns(
                v_pk["constraint_name"], table["v_name"], False, v_schema
            )
            for v_pk_column in v_pk_columns.Rows:
                pk_columns.append(v_pk_column["column_name"])

        table["pks"] = list_pk

    # 查询外键信息
    for table in table_list:
        list_fk =[]
        fks = v_database.QueryTablesForeignKeys(table["v_name"], False, v_schema)
        for v_fk in fks.Rows:
            fk_data = {}
            fk_data["name"] = v_fk["constraint_name"]
            fk_data["r_table_name"] = v_fk["r_table_name"]
            fk_data["delete_rule"] = v_fk["delete_rule"]
            fk_data["update_rule"] = v_fk["update_rule"]
            fk_columns = []
            fk_data["columns"] = fk_columns
            list_fk.append(fk_data)

            # 查询外键列信息
            v_fk_columns = v_database.QueryTablesForeignKeysColumns(
                v_fk["constraint_name"], table["v_name"], False, v_schema
            )
            for v_fk_column in v_fk_columns.Rows:
                col_name ={
                    "column_name": v_fk_column["column_name"],
                    "r_column_name": v_fk_column["r_column_name"]
                }
                fk_columns.append(col_name)
                

        table["fks"] = list_fk

    # 查询唯一约束信息
    for table in table_list:
        list_unique =[]
        uniques = v_database.QueryTablesUniques(table["v_name"], False, v_schema)
        for v_unique in uniques.Rows:
            unique_data = {}
            unique_data["name"] = v_unique["constraint_name"]
            unique_columns = []
            unique_data["columns"] = unique_columns
            list_unique.append(unique_data)

            # 查询唯一约束列信息
            v_unique_columns = v_database.QueryTablesUniquesColumns(
                v_unique["constraint_name"], table["v_name"], False, v_schema
            )
            for v_unique_column in v_unique_columns.Rows:
                unique_columns.append(v_unique_column["column_name"])

        table["uniques"] = list_unique

    # 查询索引信息
    for table in table_list:
        list_index =[]
        indexes = v_database.QueryTablesIndexes(table["v_name"], False, v_schema)
        for v_index in indexes.Rows:
            index_data = {}
            index_data["name"] = v_index["index_name"]
            index_data["uniqueness"] = v_index["uniqueness"]
            index_columns = []
            index_data["columns"] = index_columns
            list_index.append(index_data)

            # 查询索引列信息
            v_index_columns = v_database.QueryTablesIndexesColumns(
                v_index["index_name"], table["v_name"], False, v_schema
            )
            for v_index_column in v_index_columns.Rows:
                index_columns.append(v_index_column["column_name"])

        table["indexes"] = list_index
    
    # 查询函数信息
    v_functions = v_database.QueryFunctions(False, v_schema)
    list_functions = []
    for v_function in v_functions.Rows:
        function_data = {}
        function_data["name"] = v_function["name"]
        function_data["id"] = v_function["id"]
        # 查询函数定义
        function_data["definition"] = v_database.GetFunctionDefinition(v_function["id"])
        list_functions.append(function_data)
    db_info["functions"] = list_functions

    # 查询存储过程信息
    v_procedures = v_database.QueryProcedures(False, v_schema)
    list_procedures = []
    for v_procedure in v_procedures.Rows:
        procedure_data = {}
        procedure_data["name"] = v_procedure["name"]
        procedure_data["id"] = v_procedure["id"]
        # 查询存储过程定义
        procedure_data["definition"] = v_database.GetProcedureDefinition(v_procedure["id"])
        list_procedures.append(procedure_data)

    db_info["procedures"] = list_procedures

    # db_info 转成json
    db_info_content = json.dumps(db_info, indent=4)
    file_path = file_util.save_txt_file(
        DB_INFO_FILE_DIR, v_schema, "json", db_info_content
    )

    v_return["v_data"] = file_path
    return JsonResponse(v_return)
