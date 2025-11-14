# -*- coding: utf-8 -*-
import psycopg2
import time

# =================================================================================================
# LATIHAN 3: FUNGSI & KELAS (OBJECT-ORIENTED PROGRAMMING)
# =================================================================================================
# Ini adalah langkah paling fundamental untuk memahami Odoo.
# Odoo dibangun di atas prinsip Object-Oriented Programming (OOP). Setiap model data
# (seperti Produk, Kontak, Faktur) adalah sebuah "Kelas" Python.
#
# Di latihan ini, kita akan:
# 1. Mengubah kode dari Latihan 2 menjadi fungsi-fungsi yang bisa digunakan kembali.
# 2. Membuat "Kelas" Product untuk merepresentasikan data produk secara logis.
#
# Cara menjalankan file ini:
# 1. Pastikan Anda berada di dalam shell container Docker 'odoo-sandbox'.
# 2. Jalankan perintah: python 03_functions_and_classes.py
# =================================================================================================

print("===== SELAMAT DATANG DI LATIHAN 3! =====")

# --- Konfigurasi Koneksi (Sama seperti sebelumnya) ---
DB_HOST = "odoo-db"
DB_PORT = "5432"
DB_NAME = "postgres"
DB_USER = "odoo"
DB_PASSWORD = "odoo"


# -------------------------------------------------------------------------------------------------
# BAGIAN 1: MEMBUNGKUS LOGIKA KE DALAM FUNGSI
# -------------------------------------------------------------------------------------------------
# Fungsi memungkinkan kita mengelompokkan kode untuk tujuan tertentu dan memberinya nama.
# Ini membuat kode lebih bersih, mudah dibaca, dan bisa dipakai berulang kali.

def get_db_connection():
    """
    Fungsi ini bertanggung jawab HANYA untuk membuat koneksi ke database.
    Dia mencoba beberapa kali dan mengembalikan object koneksi jika berhasil.
    """
    retries = 5
    while retries > 0:
        try:
            conn = psycopg2.connect(
                host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
            )
            print("\nKoneksi ke database berhasil dibuat.")
            return conn
        except psycopg2.OperationalError:
            retries -= 1
            print(f"Koneksi gagal, mencoba lagi dalam 5 detik... ({retries} percobaan tersisa)")
            time.sleep(5)
    print("Gagal terhubung ke database.")
    return None

def setup_database(conn):
    """
    Fungsi ini memastikan tabel yang kita butuhkan sudah ada di database.
    """
    print("Menyiapkan tabel 'product_template'...")
    # Menggunakan 'with' statement memastikan cursor ditutup secara otomatis.
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS product_template (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                quantity INTEGER,
                is_active BOOLEAN DEFAULT TRUE
            );
        """)
    conn.commit()
    print("Tabel siap digunakan.")


# -------------------------------------------------------------------------------------------------
# BAGIAN 2: MEMPERKENALKAN KELAS (BLUEPRINT OBJEK)
# -------------------------------------------------------------------------------------------------
# Kelas adalah "cetak biru" untuk membuat objek. Di sini, kita membuat cetak biru
# untuk sebuah Produk. Kelas ini akan membungkus DATA (nama, kuantitas) dan
# PERILAKU (simpan ke db, cari semua produk) menjadi satu kesatuan.

class Product:
    """
    Kelas ini merepresentasikan satu record produk.
    """
    def __init__(self, name, quantity, is_active=True, id=None):
        """
        Ini adalah 'constructor'. Dipanggil setiap kali kita membuat objek Product baru.
        'self' merujuk pada objek spesifik yang sedang dibuat.
        """
        self.id = id
        self.name = name
        self.quantity = quantity
        self.is_active = is_active

    def __repr__(self):
        """
        Ini adalah representasi string dari objek, berguna untuk debugging.
        Saat kita print(objek_produk), ini yang akan ditampilkan.
        """
        return f"<Product id={self.id} name='{self.name}' quantity={self.quantity}>"

    def save(self, conn):
        """
        Ini adalah 'method' (fungsi di dalam kelas). Method ini menangani logika
        untuk menyimpan atau memperbarui produk di database.
        """
        print(f"Menyimpan produk: {self.name}...")
        with conn.cursor() as cur:
            if self.id is None:
                # Jika produk belum punya ID, berarti ini produk baru (INSERT)
                cur.execute(
                    "INSERT INTO product_template (name, quantity, is_active) VALUES (%s, %s, %s) RETURNING id",
                    (self.name, self.quantity, self.is_active)
                )
                # Ambil ID yang baru dibuat oleh database dan simpan di objek
                self.id = cur.fetchone()[0]
                print(f"Produk berhasil dibuat dengan ID: {self.id}")
            else:
                # Jika produk sudah punya ID, berarti kita mau update (UPDATE)
                cur.execute(
                    "UPDATE product_template SET name = %s, quantity = %s, is_active = %s WHERE id = %s",
                    (self.name, self.quantity, self.is_active, self.id)
                )
                print(f"Produk dengan ID: {self.id} berhasil diperbarui.")
        conn.commit()

    @classmethod
    def find_all(cls, conn):
        """
        Ini adalah 'class method'. Method ini tidak terikat pada satu objek produk,
        tapi pada kelas Product itu sendiri. Tugasnya adalah mengambil semua produk.
        """
        print("\nMencari semua produk di database...")
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, quantity, is_active FROM product_template ORDER BY id;")
            results = cur.fetchall()
            
            # Ubah setiap baris data (tuple) menjadi objek Product
            products = []
            for row in results:
                products.append(cls(id=row[0], name=row[1], quantity=row[2], is_active=row[3]))
            
            print(f"Ditemukan {len(products)} produk.")
            return products


# -------------------------------------------------------------------------------------------------
# BAGIAN 3: MENGGUNAKAN FUNGSI DAN KELAS
# -------------------------------------------------------------------------------------------------
# 'if __name__ == "__main__":' adalah standar Python untuk menandakan blok kode
# utama yang akan dieksekusi saat file ini dijalankan.

if __name__ == "__main__":
    connection = get_db_connection()
    
    if connection:
        try:
            # 1. Siapkan database
            setup_database(connection)

            # 2. Buat objek produk baru dari kelas Product
            #    Ini jauh lebih rapi daripada dictionary!
            produk_a = Product(name="Rak Buku Kayu", quantity=15)
            
            # 3. Simpan ke database dengan memanggil method-nya
            produk_a.save(connection)

            # 4. Buat dan simpan produk lain
            produk_b = Product(name="Lampu Belajar LED", quantity=30)
            produk_b.save(connection)

            # 5. Ambil SEMUA produk dari database menggunakan class method
            #    Hasilnya adalah list berisi OBJEK Product, bukan lagi data mentah.
            semua_produk_di_db = Product.find_all(connection)
            print("\n--- Daftar Produk Saat Ini ---")
            for p in semua_produk_di_db:
                print(p)
            print("-----------------------------")

            # 6. Contoh UPDATE: Ambil produk pertama, ubah stoknya, dan simpan lagi
            if semua_produk_di_db:
                produk_untuk_diupdate = semua_produk_di_db[0]
                print(f"\nMengupdate stok untuk: {produk_untuk_diupdate.name}")
                produk_untuk_diupdate.quantity = 12 # Ubah kuantitasnya
                produk_untuk_diupdate.save(connection) # Method save() akan otomatis tahu ini adalah UPDATE

                # 7. Tampilkan lagi semua produk untuk melihat perubahannya
                semua_produk_setelah_update = Product.find_all(connection)
                print("\n--- Daftar Produk Setelah Update ---")
                for p in semua_produk_setelah_update:
                    print(p)
                print("------------------------------------")

        except Exception as e:
            print(f"Terjadi error pada proses utama: {e}")
        
        finally:
            # Selalu tutup koneksi pada akhirnya
            connection.close()
            print("\nKoneksi ditutup. Latihan 3 Selesai!")
