import mysql.connector

def connect():
    try:
        db = mysql.connector.connect(host="localhost",user="root",password="root",database="informatika")

        print("Berhasil terhubung ke database")
        return db
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

