import psycopg2
import os

def get_db_connection(psql_config):
    try:
        return psycopg2.connect(
            database=psql_config["Database"],
            host=psql_config["Host"],
            user=psql_config["User"],
            password=psql_config["Password"],
            port=psql_config["Port"])
    except:
        return False

def migrate_db(db):
    curr = db.cursor()
    curr.execute("""
        create table if not exists migrate_history(
        id serial primary key,
        version varchar,
        comment varchar,
        created_at timestamp without time zone default now());
    """)
    curr.execute("select version from migrate_history order by id desc limit 1")
    res = curr.fetchone()
    if res is None:
        last_version = "0.0.0"
    else:
        last_version = res[0]   
    print(f'Current migration version: {last_version}', flush=True)
    last_version_no = get_migration_num(last_version)

    sql_files = os.listdir("migrations")
    sql_files = sorted(sql_files, key=lambda file: get_migration_num(file.split("-")[0]))
    for sql_file in sql_files:
        version, comment = sql_file.split("-")
        comment = comment.removesuffix(".sql") 
        if get_migration_num(version) > last_version_no:
             file = open("migrations/"+sql_file, mode='r')
             sql_query = file.read()
             file.close()
             curr.execute(sql_query)
             curr.execute("insert into migrate_history (version, comment) values (%s,%s)", [version, comment])
             print(f'Migration {version} applied', flush=True)

    db.commit()

def get_migration_num(version):
    nums = [int(x) for x in version.split(".")]
    return nums[0]*100 + nums[1] * 10 + nums[2]

def db_write_feedback(db, comment):
    curr = db.cursor()
    curr.execute("insert into feedback (message) values (%s)", [comment])
    db.commit()