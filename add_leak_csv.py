import csv
from chardet.universaldetector import UniversalDetector

# Kodlama algılama fonksiyonu
def detect_encoding(file_path):
    detector = UniversalDetector()
    with open(file_path, 'rb') as f:
        for line in f:
            detector.feed(line)
            if detector.done:
                break
        detector.close()
    return detector.result['encoding']

# Metin dosyasının ve hedef CSV dosyasının yolları
input_file = './15.txt'  # Kaynak metin dosyası
output_file = './15_utf8_cleaned.csv'  # Hedef CSV dosyası (UTF-8 ve temizlenmiş)

# Dosyanın kodlamasını algıla
detected_encoding = detect_encoding(input_file)
print(f"Algılanan kodlama: {detected_encoding}")

# Sorunlu karakterleri (örneğin null byte) temizle ve UTF-8'e dönüştür
with open(input_file, 'r', encoding=detected_encoding, errors='replace') as infile, open(output_file, 'w', newline='', encoding='utf-8') as outfile:
    csv_writer = csv.writer(outfile)
    for line in infile:
        # Null byte'ları ve diğer sorunlu karakterleri temizle
        clean_line = line.strip().replace('\x00', '')  # Null byte temizleniyor
        csv_writer.writerow([clean_line])

print(f"{output_file} dosyasına başarıyla dönüştürüldü! PostgreSQL için temizlendi.")

# PostgreSQL'e aktarım
import psycopg2

# PostgreSQL bağlantısı
conn = psycopg2.connect(
    dbname="",
    user="",
    password="",
    host="",
    port=""
)
cursor = conn.cursor()

# PostgreSQL'e \COPY ile aktarım
try:
    with open(output_file, 'r', encoding='utf-8') as file:
        cursor.copy_expert("COPY leaks(data) FROM STDIN CSV", file)
    conn.commit()
    print("Veriler PostgreSQL'e başarıyla aktarıldı!")
except Exception as e:
    print(f"PostgreSQL'e aktarım sırasında bir hata oluştu: {e}")
finally:
    cursor.close()
    conn.close()
