import json
import os
import pymysql
from genson import SchemaBuilder
from jsonschema.validators import validate


# Json Schema
def generate_jsonschema(obj, by_file: str | None = None):
    builder = SchemaBuilder()
    builder.add_object(obj)
    schema = builder.to_schema()

    if by_file:
        with open(by_file, "w") as f:
            json.dump(schema, f)
        return
    return schema


def validate_jsonschema(obj, schema, by_file: str | None = None):
    if not schema and not by_file:
        raise Exception("We need schema or by_file")

    if by_file:
        with open(by_file) as f:
            schema = json.load(f)
    try:
        validate(instance=obj, schema=schema)
        return True
    except Exception:
        return False


# MySQL
def execute_sql(sql: str):
    cfg_type = str | None

    host: cfg_type = os.environ.get("mysql_host")
    port: cfg_type = os.environ.get("mysql_port")
    user: cfg_type = os.environ.get("mysql_user")
    password: cfg_type = os.environ.get("mysql_password")
    database: cfg_type = os.environ.get("mysql_database")

    if not host or not port or not user or not password or not database:
        raise Exception("Please refine the MySQL in the local environment variable")

    try:
        conn = pymysql.connect(
            host=host, port=int(port), user=user, password=password, database=database, charset="utf8mb4"
        )
    except Exception:
        raise Exception("DB connection failure")

    cursor = conn.cursor()
    cursor.execute(sql)
    record = cursor.fetchone()

    conn.close()
    return record
