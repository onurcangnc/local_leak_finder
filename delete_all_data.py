import psycopg2

def clear_table():
    try:
        # Veritabanı bağlantısı
        conn = psycopg2.connect(
            dbname="railway",
            user="postgres",
            password="GIwrtWvJmhTxqjokahbkaXmFAypVsYtu",
            host="viaduct.proxy.rlwy.net",
            port="39942"
        )
        cursor = conn.cursor()

        # Verileri temizleme
        cursor.execute("TRUNCATE TABLE leaks RESTART IDENTITY;")
        conn.commit()

        print("Tüm veriler başarıyla silindi.")

    except Exception as e:
        print(f"[HATA] {e}")

    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    clear_table()
