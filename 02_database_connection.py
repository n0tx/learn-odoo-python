# -*- coding: utf-8 -*-
import os
import psycopg2
import time

# =================================================================================================
# LATIHAN 2: KONEKSI & OPERASI DASAR DATABASE
# =================================================================================================
# Di latihan ini, kita akan menghubungkan Python ke database PostgreSQL yang berjalan
# di container lain. Ini adalah simulasi dari apa yang Odoo lakukan setiap saat.
#
# Cara menjalankan file ini:
# 1. Pastikan Anda berada di dalam shell container Docker 'odoo-sandbox'.
# 2. Jalankan perintah: python 02_database_connection.py
# =================================================================================================

print("===== SELAMAT DATANG DI LATIHAN 2! =====")

# --- Konfigurasi Koneksi ---
# Informasi ini kita dapatkan dari bagaimana kita menjalankan container 'odoo-db'.
# Karena kedua container berada di jaringan Docker yang sama ('odoo-learn-net'),
# kita bisa menggunakan nama service ('odoo-db') sebagai hostname.
DB_HOST = "odoo-db"
DB_PORT = "5432"  # Port default PostgreSQL
DB_NAME = "postgres"
DB_USER = "odoo"
DB_PASSWORD = "odoo"

# Fungsi untuk mencoba koneksi berulang kali
def get_connection():
    """Mencoba terhubung ke database, mencoba beberapa kali jika gagal."""
    retries = 5
    while retries > 0:
        try:
            print("\nMencoba terhubung ke database...")
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            print("Koneksi berhasil!")
            return conn
        except psycopg2.OperationalError as e:
            print(f"Koneksi gagal: {e}")
            retries -= 1
            print(f"Mencoba lagi dalam 5 detik... ({retries} percobaan tersisa)")
            time.sleep(5)
    print("Gagal terhubung ke database setelah beberapa kali percobaan.")
    return None

# Dapatkan koneksi
conn = get_connection()

# Jika koneksi tidak berhasil, hentikan eksekusi
if not conn:
    print("\n===== LATIHAN 2 GAGAL! Tidak bisa melanjutkan tanpa koneksi database. =====")
else:
    # 'cursor' adalah objek yang kita gunakan untuk mengirim perintah ke database.
    cur = conn.cursor()

    try:
        # --- OPERASI 1: Membuat Tabel ---
        # Kita akan membuat tabel sederhana untuk menyimpan produk.
        # 'IF NOT EXISTS' memastikan kita tidak error jika tabel sudah ada.
        print("\nMembuat tabel 'product_template' jika belum ada...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS product_template (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                quantity INTEGER,
                is_active BOOLEAN DEFAULT TRUE
            );
        """)
        print("Tabel berhasil diperiksa/dibuat.")

        # --- OPERASI 2: Memasukkan Data (INSERT) ---
        # Kita gunakan dictionary (seperti di latihan 1) untuk menampung data.
        produk_baru = {
            'name': 'Kursi Kantor Ergonomis',
            'quantity': 25,
            'is_active': True
        }
        
        print(f"\nMemasukkan produk baru: {produk_baru['name']}")
        # Tanda %s adalah placeholder untuk mencegah SQL Injection.
        cur.execute(
            "INSERT INTO product_template (name, quantity, is_active) VALUES (%s, %s, %s)",
            (produk_baru['name'], produk_baru['quantity'], produk_baru['is_active'])
        )
        print("Produk berhasil dimasukkan.")

        # --- OPERASI 3: Mengambil Data (SELECT) ---
        print("\nMengambil semua data dari 'product_template'...")
        cur.execute("SELECT id, name, quantity, is_active FROM product_template;")
        
        # cur.fetchall() akan mengembalikan list of tuples.
        # Contoh: [(1, 'Kursi Kantor', 25, True), (2, 'Meja Rapat', 10, True)]
        semua_produk = cur.fetchall()
        
        print("\n--- DAFTAR PRODUK DI DATABASE ---")
        for produk in semua_produk:
            # produk di sini adalah sebuah tuple, misal: (1, 'Kursi Kantor', 25, True)
            print(f"ID: {produk[0]}, Nama: {produk[1]}, Stok: {produk[2]}, Aktif: {produk[3]}")
        print("---------------------------------")

        # --- PENTING: COMMIT Perubahan ---
        # Perintah INSERT/UPDATE/DELETE tidak akan disimpan permanen di database
        # sampai kita menjalankan conn.commit().
        conn.commit()
        print("\nPerubahan telah di-commit ke database.")

    except Exception as e:
        print(f"\nTerjadi error: {e}")
        # Jika terjadi error, batalkan semua perubahan sejak commit terakhir.
        conn.rollback()
        print("Perubahan di-rollback.")

    finally:
        # --- PENTING: Selalu tutup cursor dan koneksi ---
        print("\nMenutup cursor dan koneksi...")
        cur.close()
        conn.close()
        print("Koneksi ditutup.")
        print("\n===== LATIHAN 2 SELESAI! =====")
