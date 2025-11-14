# -*- coding: utf-8 -*-

"""
File Latihan 04: Pengenalan Odoo Model (Simulasi)

TUJUAN:
Memahami konsep dasar Object-Relational Mapping (ORM) di Odoo.
Di Odoo, kita tidak menulis query SQL secara manual (seperti SELECT, INSERT).
Sebagai gantinya, kita mendefinisikan class Python yang secara otomatis
dipetakan (mapped) ke tabel database. Class ini disebut "Model".

KONSEP UTAMA:
1.  Model Class: Sebuah class Python yang mewarisi (inherits) dari `models.Model`.
    Nama class biasanya dalam format CamelCase (misal: `ProductProduct`).
2.  Atribut `_name`: Atribut khusus yang mendefinisikan nama teknis model,
    yang juga menjadi nama tabel di database (dengan `.` diganti `_`).
    Contoh: `_name = 'product.product'` akan menjadi tabel `product_product`.
3.  Fields: Atribut di dalam class Model yang merupakan instance dari class Field
    (misal: `fields.Char`, `fields.Integer`). Ini akan menjadi kolom di tabel.

PENJELASAN SIMULASI INI:
Karena kita belum menginstal Odoo, file ini membuat class "tiruan" atau "mock"
bernama `Model`, `Field`, `Char`, `Integer`, dan `Float` untuk meniru cara kerja
Odoo. Ini membantu kita fokus pada SINTAKS dan STRUKTUR pendefinisian Model
tanpa kompleksitas framework Odoo yang sebenarnya.
"""

# --- BAGIAN SIMULASI FRAMEWORK ODOO ---
# Di Odoo asli, ini akan menjadi: `from odoo import models, fields`

class Field:
    """Kelas dasar tiruan untuk semua jenis Field."""
    def __init__(self, string="", help=""):
        self.string = string
        self.help = help
        self.name = None # Akan diisi secara otomatis nanti

    def __repr__(self):
        return f"<{self.__class__.__name__} '{self.name}' >"

class Char(Field):
    """Tiruan untuk fields.Char (untuk teks)."""
    pass

class Integer(Field):
    """Tiruan untuk fields.Integer (untuk angka bulat)."""
    pass

class Float(Field):
    """Tiruan untuk fields.Float (untuk angka desimal)."""
    pass

class Model:
    """
    Kelas dasar tiruan untuk `models.Model`.
    Menggunakan 'magic' Python (`__init_subclass__`) untuk secara otomatis
    mendeteksi semua field yang didefinisikan di dalam class anak (subclass).
    """
    _fields = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._fields = {}
        # Cari semua atribut yang merupakan instance dari Field
        for attr_name, attr_value in cls.__dict__.items():
            if isinstance(attr_value, Field):
                attr_value.name = attr_name # Beri tahu field namanya sendiri
                cls._fields[attr_name] = attr_value
        print(f"--- Model '{cls._name}' berhasil didaftarkan dengan {len(cls._fields)} fields ---")


# --- BAGIAN PENGEMBANGAN MODEL ODOO (YANG SEBENARNYA ANDA TULIS) ---

class ProductTemplate(Model):
    """
    Ini adalah contoh Model Odoo.
    Kita mendefinisikan sebuah produk.
    """
    # Atribut _name wajib ada. Ini akan menjadi tabel 'product_template' di DB.
    _name = 'product.template'

    # Mendefinisikan fields (kolom tabel)
    # Format: nama_field = TipeField(label_untuk_user, bantuan_untuk_user)
    name = Char(string="Nama Produk", help="Nama yang akan ditampilkan kepada pelanggan.")
    description = Char(string="Deskripsi", help="Deskripsi detail tentang produk.")
    quantity_on_hand = Integer(string="Stok", help="Jumlah stok yang tersedia saat ini.")
    list_price = Float(string="Harga Jual", help="Harga jual standar produk.")


# --- BAGIAN DEMONSTRASI (UNTUK MEMERIKSA HASIL SIMULASI) ---

if __name__ == "__main__":
    print("\nAnalisis Hasil Simulasi Model 'ProductTemplate':")
    print("==============================================")
    print(f"Nama Tabel di Database: {ProductTemplate._name.replace('.', '_')}")
    print("\nFields yang terdeteksi:")

    # Kita bisa mengakses kamus `_fields` yang dibuat oleh class Model tiruan kita
    for field_name, field_obj in ProductTemplate._fields.items():
        print(
            f"- Nama Field: {field_name}\n"
            f"  Tipe Data : {type(field_obj).__name__}\n"
            f"  Label UI  : '{field_obj.string}'\n"
            f"  Help Text : '{field_obj.help}'\n"
        )

    print("\nKESIMPULAN:")
    print("Kita berhasil mendefinisikan struktur Model ProductTemplate dengan 4 kolom.")
    print("Ini adalah langkah pertama dalam pengembangan Odoo: mendefinisikan data.")
    print("Langkah selanjutnya adalah belajar bagaimana membuat, membaca, mengubah, dan menghapus (CRUD) data menggunakan Model ini.")
