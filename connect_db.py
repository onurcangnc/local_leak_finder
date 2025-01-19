import psycopg2

try:
    conn = psycopg2.connect(
        dbname="postgres",
        user="botuser",
        password="admin",
        host="localhost",
        port="5432"  # PostgreSQL'in varsayılan portu
    )
    print("Bağlantı başarılı!")
    conn.close()
except Exception as e:
    print(f"Bağlantı hatası: {e}")
