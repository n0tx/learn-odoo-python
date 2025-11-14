# -*- coding: utf-8 -*-

"""
File Latihan 05: Membuat Record (Create) dengan ORM

TUJUAN:
Memahami cara membuat data baru (record) menggunakan metode ORM `create()`.
Ini adalah operasi 'Create' dalam CRUD (Create, Read, Update, Delete).

KONSEP UTAMA:
1.  Metode `create()`: Ini adalah metode standar pada semua Model Odoo.
    Ia menerima sebuah dictionary Python di mana:
    -   `key` adalah nama teknis dari field (misal: 'name', 'list_price').
    -   `value` adalah nilai yang ingin Anda simpan untuk field tersebut.
2.  Return Value: Metode `create()` mengembalikan sebuah "recordset", yaitu
    sebuah objek yang merepresentasikan satu atau lebih record yang baru dibuat.
    Untuk saat ini, kita akan simulasikan ia mengembalikan dictionary dari
    data yang baru saja disimpan.
3.  Database Tiruan: Untuk mensimulasikan penyimpanan data, kita akan menambahkan
    sebuah list sederhana (`_data`) ke dalam class Model tiruan kita. Setiap
    elemen dalam list ini akan merepresentasikan satu baris (record) di tabel.

PENJELASAN SIMULASI INI:
Kita akan memperluas simulasi dari file sebelumnya. Class `Model` tiruan kita
sekarang akan memiliki "database" sendiri (sebuah list) dan implementasi
sederhana dari metode `create()`.
"""

import pprint # Import modul untuk "pretty-printing" agar output lebih rapi

# --- BAGIAN SIMULASI FRAMEWORK ODOO ---

class Field:
    def __init__(self, string="", help=""):
        self.string = string
        self.help = help
        self.name = None

    def __repr__(self):
        return f"<{self.__class__.__name__} '{self.name}'>"

class Char(Field): pass
class Integer(Field): pass
class Float(Field): pass

class Model:
    _fields = {}
    _data = [] # << BARU: "Database" tiruan untuk menyimpan semua record

    def __init_subclass__(cls, **kwargs):
        """Mendeteksi fields saat class didefinisikan."""
        super().__init_subclass__(**kwargs)
        cls._fields = {}
        cls._data = [] # Setiap model punya data-nya sendiri
        for attr_name, attr_value in cls.__dict__.items():
            if isinstance(attr_value, Field):
                attr_value.name = attr_name
                cls._fields[attr_name] = attr_value
        print(f"--- Model '{cls._name}' siap digunakan ---")

    @classmethod
    def create(cls, values):
        """
        Simulasi dari metode ORM `create()`.
        'values' adalah sebuah dictionary, misal: {'name': 'Meja', 'list_price': 150.0}
        """
        print(f"\nMemanggil {cls.__name__}.create() dengan data:")
        pprint.pprint(values)

        # Validasi sederhana: pastikan semua field yang diberikan ada di model
        for field_name in values.keys():
            if field_name not in cls._fields:
                print(f"-> Peringatan: Field '{field_name}' tidak ada di model '{cls._name}'. Diabaikan.")
                continue

        # Menambahkan ID unik (di Odoo asli ini adalah auto-increment integer)
        new_id = len(cls._data) + 1
        record_data = {'id': new_id}
        record_data.update(values)

        # "Menyimpan" record ke database tiruan kita
        cls._data.append(record_data)
        print(f"-> Sukses! Record baru dibuat dengan ID: {new_id}")

        # Di Odoo asli, ini mengembalikan objek recordset. Kita kembalikan dict-nya.
        return record_data

# --- BAGIAN PENGEMBANGAN MODEL ODOO ---

class ProductTemplate(Model):
    _name = 'product.template'

    name = Char(string="Nama Produk")
    quantity_on_hand = Integer(string="Stok")
    list_price = Float(string="Harga Jual")


# --- BAGIAN DEMONSTRASI ---

if __name__ == "__main__":
    print("===== MULAI DEMONSTRASI PEMBUATAN RECORD ====")

    # 1. Membuat record pertama
    produk_1 = ProductTemplate.create({
        'name': 'Kursi Kantor Ergonomis',
        'quantity_on_hand': 25,
        'list_price': 1250000.0,
    })

    # 2. Membuat record kedua
    produk_2 = ProductTemplate.create({
        'name': 'Meja Belajar Kayu Jati',
        'quantity_on_hand': 10,
        'list_price': 850000.0,
    })

    # 3. Membuat record ketiga dengan field yang tidak ada (untuk tes validasi)
    produk_3 = ProductTemplate.create({
        'name': 'Lampu LED Meja',
        'list_price': 150000.0,
        'warna': 'Putih' # Field ini tidak ada di model ProductTemplate
    })


    print("\n\n===== ANALISIS HASIL AKHIR ====")
    print(f"Isi 'database' tiruan untuk model '{ProductTemplate._name}':")
    # Mencetak isi "database" kita dengan format yang lebih rapi
    pprint.pprint(ProductTemplate._data)

    print("\nKESIMPULAN:")
    print(f"Kita berhasil membuat {len(ProductTemplate._data)} record baru di model ProductTemplate.")
    print("Metode `create()` adalah cara standar untuk memasukkan data baru ke Odoo.")
    print("Langkah selanjutnya adalah belajar bagaimana membaca (Read/Search) data yang sudah ada ini.")
