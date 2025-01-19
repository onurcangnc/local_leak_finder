import psycopg2

def import_single_column(file_path):
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user="botuser",
            password="admin",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()

        with open(file_path, "r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.replace("\x00", "").strip()  # NUL karakterleri temizle, boşlukları sil
                if line:
                    try:
                        cursor.execute("INSERT INTO leaks (data) VALUES (%s)", (line,))
                    except Exception as e:
                        print(f"[HATA-DB] Satır {line_number} -> {line}\nDetay: {e}")

        conn.commit()
        print("Veriler başarıyla tabloya eklendi.")

    except Exception as e:
        print(f"[BAĞLANTI HATASI] {e}")

    finally:
        if conn:
            cursor.close()
            conn.close()

# Kullanım:
if __name__ == "__main__":
    import_single_column("12.txt")
