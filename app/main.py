from databasedriver import DatabaseDriver

from helpers import DB_NAME, DB_HOST, DB_PORT, DB_PASSWORD, DB_USER, DB_TABLE_MET_HISTORICAL

db = DatabaseDriver(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)

df = db.load_db_table(table_name=DB_TABLE_MET_HISTORICAL)


