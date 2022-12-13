import pymysql


HOST = 'db-sie-prod.c6r9vkodxz44.us-east-1.rds.amazonaws.com'
USER = 'speakerspdf'
PASS = 'speakerspdf'
DB =   'speakerspdf'


def get_conexion_pdf_cursor():
    return pymysql.connect(
        host=HOST,
        user=USER,
        passwd=PASS,
        cursorclass=pymysql.cursors.DictCursor,
        db=DB
    )
