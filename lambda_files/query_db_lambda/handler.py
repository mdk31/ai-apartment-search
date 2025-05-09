import json
import boto3
import psycopg2
import os
from aws_secretsmanager_caching import SecretCache, SecretCacheConfig
from psycopg2.extras import RealDictCursor
from psycopg2 import sql
import pdb


SCHEMA_KEY = "allowed_schema.json"

ALLOWED_FUNCTIONS = {
    "ST_DWithin": lambda args: sql.SQL("ST_DWithin({}, {}, {})").format(*args),
    "ST_MakePoint": lambda args: sql.SQL("ST_MakePoint({}, {})").format(*args)
}

secrentsclient = boto3.client('secretsmanager')
s3client = boto3.client('s3')
cache = SecretCache(config=SecretCacheConfig(), client=secrentsclient)

def get_config():
    return {
        'host': os.environ['DB_HOST'],
        'db_secret': os.environ['DB_SECRET']
    }
#     DB_HOST = 
# DB_PORT = os.environ['DB_PORT']
# DB_SECRET = 
# DB_NAME = os.environ['DB_NAME']
# SCHEMA_BUCKET = os.environ["SCHEMA_BUCKET"]

def build_function_call(func_dict, from_tables, allowed_schema):
    func_name = func_dict['name']
    args = func_dict['args']
    if func_name not in ALLOWED_FUNCTIONS:
        raise ValueError(f"Function {func_name} not allowed")
    
    formatted_args = []
    for arg in args:
        if isinstance(arg, dict) and 'name' in arg:
            formatted_args.append(build_function_call(arg, from_tables, allowed_schema))
        elif isinstance(arg, str):
            formatted_args.append(validate_column(arg, from_tables, allowed_schema))
        else:
            formatted_args.append(sql.Placeholder())
    
    return ALLOWED_FUNCTIONS[func_name](formatted_args)

def build_safe_sql(query_json, allowed_schema):
    select_fields = query_json['select']
    from_tables = query_json['from']
    joins = query_json.get('joins', [])
    where = query_json.get('where', {})
    group_by = query_json.get('GROUPBY', {})
    having = query_json.get('HAVING', {})

    select_sql = sql.SQL(', ').join([
        validate_column(col, from_tables, allowed_schema) for col in select_fields
    ])

    from_sql = sql.Identifier(from_tables[0])
    join_sql_parts = []

    for join in joins:
        join_type = join.get('type', 'INNER').upper() # keep SQL code uppercase
        table = join['table']
        if table not in allowed_schema:
            raise ValueError(f"Invalid join table: {table}")
        on_clause = join['on']
        join_sql_parts.append(sql.SQL(" {join_type} JOIN {} ON {}").format(
            sql.Identifier(join_type),
            sql.Identifier(table),
            build_function_call(on_clause, from_tables + [table], allowed_schema)
        ))
    
    where_clauses = []
    params = []
    for col, cond in where.items():
        for operator, val in cond.items():
            col_sql = validate_column(col, from_tables, allowed_schema)
            where_clauses.append(sql.SQL("{} {} %s").format(
                col_sql, sql.SQL(operator)
            ))
            params.append(val)

    group_sql = sql.SQL(', ').join([
        validate_column(col, from_tables, allowed_schema) for col in group_by
    ]) if group_by else None

    having_clauses = []
    for cond in having:
        agg = cond['aggregate']
        col = cond['column']
        operator = cond['operator']
        value = cond['value']

        # Handle COUNT(*)
        if col == "*":
            col_sql = sql.SQL("*")
        else:
            col_sql = validate_column(col, from_tables, allowed_schema)

        having_expr = sql.SQL("{}({}) {} %s").format(
            sql.SQL(agg),
            col_sql,
            sql.SQL(operator)
        )
        having_clauses.append(having_expr)
        params.append(value)

        
    query_parts = [
        sql.SQL("SELECT "), select_sql,
        sql.SQL("FROM "), from_sql
    ]

    if join_sql_parts:
        query_parts += join_sql_parts
    if where_clauses:
        query_parts += [sql.SQL("WHERE "), sql.SQL(" AND ").join(where_clauses)]
    
    return sql.Composed(query_parts), params

def get_db_connection():
    user, password = get_db_credentials()
    return psycopg2.connect(
        dbname=DB_NAME,
        user=user,
        password=password,
        host=DB_HOST,
        port=DB_PORT
    )


def get_db_credentials():
    secret_name = os.environ['DBSECRET']
    secret = json.loads(cache.get_secret_string(secret_name))
    return secret['username'], secret['password']

def load_allowed_schema():
    obj = s3client.get_object(Bucket=SCHEMA_BUCKET, key=SCHEMA_KEY)
    return json.loads(obj['Body'].read())

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        action = body.get('action')

        if action == 'refresh_schema':
            refresh_schema_from_db()
            return {
                'statusCode': 200,
                'body': json.dumps({"message": "Schemea fetched and saved to S3"})
            }
        
        query_json = body['query_json']
        allowed_schema = load_allowed_schema()
        query, params = build_safe_sql(query_json, allowed_schema)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, params)
        results = cur.fetchall()
        cur.close()
        conn.close()

        return {
            'statusCode': 200,
            'body': json.dumps({"results": results})
        }


    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }



def refresh_schema_from_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute()

    #     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute("""
#         SELECT table_name, column_name
#         FROM information_schema.columns
#         WHERE table_schema = 'public'
#     """)
#     schema = {}
#     for table, column in cur.fetchall():
#         schema.setdefault(table, set()).add(column)
#     cur.close()
#     conn.close()

#     schema_json = {k: list(v) for k, v in schema.items()}

#     s3.put_object(
#         Bucket=SCHEMA_BUCKET,
#         Key=SCHEMA_KEY,
#         Body=json.dumps(schema_json)
#     )

#     return schema_json




def validate_column(col: str, from_tables: list[str], allowed_schema) -> sql.Composable:
    if '.' in col:
        table, field = col.split('.', 1)
        if table not in allowed_schema or field not in allowed_schema[table]:
            raise ValueError(f"Undefined column: {col}")
        return sql.Identifier(table, field)
        
    candidates = [t for t in from_tables if col in allowed_schema.get(t, set())]
    if len(candidates) != 1:
        raise ValueError(f"Ambiguous column: {col}")
    return sql.Identifier(candidates[0], col)
        




