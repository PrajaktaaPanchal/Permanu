# import pymysql
# import os

# def get_connection():
#     try:
#         # for Docker
#         # connection = pymysql.connect(host='ctidb', user='root', password='Root@123', database='cti', port=3306, cursorclass=pymysql.cursors.DictCursor
#         # )


#         connection = pymysql.connect(
#         host='192.168.60.210',
#         user="new_cti",
#         password="Cti@123",
#         database='cti',
#         port=3306,
#         cursorclass=pymysql.cursors.DictCursor
#         )

#         # cur = connection.cursor()
#         return connection
#     except pymysql.MySQLError as e:
#         raise Exception("Database connection failed") from e



import pymysql

def get_connection():
    try:
        connection = pymysql.connect(
            host='192.168.60.87',
            user='Project_track',
            password='Tracker@123',
            database='projecttracker',
            port=3306,
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except pymysql.MySQLError as e:
        raise Exception("Database connection failed") from e

def show_tables():
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            for table in tables:
                print(table)  
    finally:
        conn.close()