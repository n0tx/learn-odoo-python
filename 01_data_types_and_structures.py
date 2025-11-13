# -*- coding: utf-8 -*-

# =================================================================================================
# LATIHAN 1: TIPE DATA & STRUKTUR DATA FUNDAMENTAL
# =================================================================================================
# Ini adalah file latihan pertama kita. Fokusnya adalah pada tipe data dasar
# dan struktur data yang akan Anda gunakan SETIAP HARI saat developing di Odoo.
#
# Cara menjalankan file ini:
# 1. Pastikan Anda berada di dalam shell container Docker kita.
# 2. Jalankan perintah: python 01_data_types_and_structures.py
# =================================================================================================

print("===== SELAMAT DATANG DI LATIHAN 1! =====")

# -------------------------------------------------------------------------------------------------
# BAGIAN 1: TIPE DATA DASAR
# -------------------------------------------------------------------------------------------------
# Python memiliki beberapa tipe data dasar. Tiga yang paling sering Anda temui di Odoo adalah:
# String (teks), Integer (angka bulat), dan Boolean (Benar/Salah).

# 1. String (str) - Untuk data teks seperti nama, deskripsi, alamat.
#    Di Odoo, ini merepresentasikan field Char, Text, atau Selection.
nama_produk = "Meja Kantor"
deskripsi = 'Meja ini terbuat dari kayu jati pilihan.'
print(f"\nNama Produk: {nama_produk} (Tipe: {type(nama_produk)})")

# 2. Integer (int) - Untuk angka bulat seperti jumlah, ID, atau urutan.
#    Di Odoo, ini merepresentasikan field Integer.
jumlah_stok = 15
id_produk = 101
print(f"Jumlah Stok: {jumlah_stok} (Tipe: {type(jumlah_stok)})")

# 3. Float (float) - Untuk angka desimal seperti harga, berat, atau persentase.
#    Di Odoo, ini merepresentasikan field Float.
harga_satuan = 750000.50
print(f"Harga Satuan: {harga_satuan} (Tipe: {type(harga_satuan)})")

# 4. Boolean (bool) - Hanya memiliki dua nilai: True atau False.
#    Sangat penting untuk logika, seperti menandai apakah sebuah produk aktif atau tidak.
#    Di Odoo, ini merepresentasikan field Boolean.
apakah_aktif = True
sudah_terjual = False
print(f"Apakah Produk Aktif? {apakah_aktif} (Tipe: {type(apakah_aktif)})")


# -------------------------------------------------------------------------------------------------
# BAGIAN 2: STRUKTUR DATA KUNCI - LIST & DICTIONARY
# -------------------------------------------------------------------------------------------------
# Ini adalah bagian PALING PENTING dari latihan ini. List dan Dictionary adalah
# tulang punggung dari hampir semua operasi data di Odoo.

# 1. List - Kumpulan data yang TERURUT.
#    Di Odoo, Anda akan sering menerima hasil query database dalam bentuk list of records.
#    List dibuat dengan kurung siku [].

daftar_warna = ["Merah", "Putih", "Hitam"]
print(f"\nDaftar Warna yang Tersedia: {daftar_warna}")

# Mengakses item dalam list (dimulai dari indeks 0)
warna_pertama = daftar_warna[0]
print(f"Warna pertama adalah: {warna_pertama}")

# Menambah item ke list
daftar_warna.append("Coklat")
print(f"Daftar warna setelah ditambah: {daftar_warna}")

# Looping (perulangan) pada list - operasi yang sangat umum
print("\nLooping melalui semua warna:")
for warna in daftar_warna:
    print(f"- {warna}")


# 2. Dictionary (dict) - Kumpulan data dalam bentuk pasangan KEY-VALUE (kunci-nilai).
#    INI ADALAH STRUKTUR DATA PALING KRUSIAL DI ODOO.
#    - Saat membuat record baru di Odoo, Anda memberikan dictionary.
#    - Saat meng-update record, Anda memberikan dictionary.
#    - Definisi field, view, dan action di Odoo semuanya menggunakan struktur mirip dictionary.
#    Dictionary dibuat dengan kurung kurawal {}.

# Contoh: merepresentasikan satu produk sebagai sebuah dictionary
produk_dict = {
    'name': "Kursi Gaming",
    'stock': 10,
    'price': 1250000.00,
    'is_active': True
}

print(f"\nData Produk (Dictionary): {produk_dict}")

# Mengakses nilai menggunakan kuncinya (key)
nama_dari_dict = produk_dict['name']
stok_dari_dict = produk_dict['stock']
print(f"Mengambil nama dari dict: {nama_dari_dict}")
print(f"Mengambil stok dari dict: {stok_dari_dict}")

# Mengubah nilai dalam dictionary
print("Stok sebelum diubah:", produk_dict['stock'])
produk_dict['stock'] = 8  # Misal, 2 buah terjual
print("Stok setelah diubah:", produk_dict['stock'])

# Menambah key-value baru
produk_dict['category'] = "Furniture"
print(f"Dictionary setelah ditambah kategori: {produk_dict}")


# -------------------------------------------------------------------------------------------------
# BAGIAN 3: KOMBINASI LIST DAN DICTIONARY
# -------------------------------------------------------------------------------------------------
# Di dunia nyata Odoo, Anda akan sering bekerja dengan "List of Dictionaries".
# Bayangkan Anda mengambil data beberapa produk dari database.

daftar_produk = [
    {
        'id': 1,
        'name': "Meja Belajar",
        'stock': 20,
        'is_active': True
    },
    {
        'id': 2,
        'name': "Lampu LED",
        'stock': 50,
        'is_active': True
    },
    {
        'id': 3,
        'name': "Papan Tulis",
        'stock': 0,
        'is_active': False
    }
]

print("\n===== Bekerja dengan List of Dictionaries ====")
print("Looping melalui daftar produk:")

# Looping untuk memproses setiap produk
total_stok = 10
for produk in daftar_produk:
    # 'produk' di sini adalah sebuah dictionary
    nama = produk['name']
    stok = produk['stock']
    status = "Aktif" if produk['is_active'] else "Tidak Aktif"

    print(f"- Produk: {nama}, Stok: {stok}, Status: {status}")

    # Contoh operasi: menjumlahkan total stok
    total_stok += stok # sama dengan total_stok = total_stok + stok

print(f"\nTotal stok dari semua produk: {total_stok}")


print("\n===== LATIHAN 1 SELESAI! =====")
print("Silakan coba ubah nilai-nilai di atas dan jalankan lagi file ini.")
