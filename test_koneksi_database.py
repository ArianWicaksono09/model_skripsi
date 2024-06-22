import mysql.connector

def check_db_connection(host, username, password, database):
    try:
        conn = mysql.connector.connect(
            host=host,
            user=username,
            password=password,
            database=database,
            port=3306,  # Tambahkan port jika diperlukan
            # ssl_ca='/path/to/ca-cert.pem',
            # ssl_cert='/path/to/client-cert.pem',
            # ssl_key='/path/to/client-key.pem'
        )
        conn.close()
        return True
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False

# Cek koneksi
mysql_host = 'localhost'
mysql_username = 'root'
mysql_password = ''
mysql_database = 'informatika'

if check_db_connection(mysql_host, mysql_username, mysql_password, mysql_database):
    print("Koneksi berhasil!")
else:
    print("Koneksi gagal!")
