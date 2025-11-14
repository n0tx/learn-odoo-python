# -*- coding: utf-8 -*-
import psycopg2
import psycopg2.extras

# ==================================================================================================
# SIMULASI ODOO ORM FRAMEWORK (BAGIAN INI JANGAN DIUBAH)
# ==================================================================================================
# Ini adalah versi sederhana dari cara kerja Odoo ORM.
# Tujuannya adalah untuk memahami konsepnya tanpa perlu instalasi Odoo lengkap.

class Database:
    """Kelas untuk mengelola koneksi database."""
    _connection = None

    @classmethod
    def get_connection(cls):
        if cls._connection is None:
            try:
                cls._connection = psycopg2.connect(
                    dbname="postgres",
                    user="odoo",
                    password="odoo",
                    host="odoo-db",
                    port="5432"
                )
            except psycopg2.OperationalError as e:
                print(f"Gagal terhubung ke database: {e}")
                print("Pastikan kontainer 'odoo-db' sudah berjalan.")
                exit()
        return cls._connection

class Registry(dict):
    """Mendaftarkan semua model yang ada."""
    def __init__(self):
        super().__init__()

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        return value

    def register(self, cls):
        """Decorator untuk mendaftarkan class Model."""
        self[cls._name] = cls
        return cls

registry = Registry()

class Field:
    """Kelas dasar untuk semua tipe field."""
    def __init__(self, string=""):
        self.string = string

class Char(Field):
    """Untuk tipe data teks/string."""
    pass

class Float(Field):
    """Untuk tipe data angka desimal."""
    pass

class Model:
    """Kelas dasar untuk semua model, merepresentasikan sebuah tabel di database."""
    _name = None
    _table = None
    _fields = None
    _auto = True # Asumsi ID dibuat otomatis

    def __init__(self, env, record_id=None, values=None):
        self.env = env
        self.id = record_id
        if values:
            for key, value in values.items():
                setattr(self, key, value)

    @classmethod
    def _init_model(cls):
        """Mempersiapkan model, field, dan tabel database."""
        cls._table = cls._name.replace('.', '_')
        cls._fields = {name: field for name, field in cls.__dict__.items() if isinstance(field, Field)}
        cls._create_table()

    @classmethod
    def _create_table(cls):
        """Membuat tabel di database jika belum ada."""
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        columns = ["id SERIAL PRIMARY KEY"]
        for name, field in cls._fields.items():
            if isinstance(field, Char):
                col_type = "VARCHAR(255)"
            elif isinstance(field, Float):
                col_type = "FLOAT"
            else:
                col_type = "VARCHAR(255)"
            columns.append(f"{name} {col_type}")
        
        query = f"CREATE TABLE IF NOT EXISTS {cls._table} ({', '.join(columns)})"
        cursor.execute(query)
        conn.commit()
        cursor.close()

    @classmethod
    def create(cls, values):
        """Membuat record baru di database (Operasi CREATE)."""
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        columns = []
        placeholders = []
        data = []
        
        for name, value in values.items():
            if name in cls._fields:
                columns.append(name)
                placeholders.append("%s")
                data.append(value)
        
        query = f"INSERT INTO {cls._table} ({', '.join(columns)}) VALUES ({', '.join(placeholders)}) RETURNING id"
        cursor.execute(query, tuple(data))
        new_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        
        print(f"Record baru dibuat di '{cls._name}' dengan ID: {new_id}")
        return cls(cls, new_id, values)

    @classmethod
    def search(cls, domain):
        """Mencari record berdasarkan kriteria/domain (Operasi READ)."""
        conn = Database.get_connection()
        # Menggunakan DictCursor untuk mendapatkan hasil sebagai dictionary
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        query = f"SELECT * FROM {cls._table}"
        where_clauses = []
        params = []

        if domain:
            for condition in domain:
                field, operator, value = condition
                where_clauses.append(f"{field} {operator} %s")
                params.append(value)
            query += " WHERE " + " AND ".join(where_clauses)

        cursor.execute(query, tuple(params))
        results = cursor.fetchall()
        cursor.close()
        
        # Mengubah hasil query menjadi list of model instances
        records = [cls(cls, record['id'], dict(record)) for record in results]
        return records

    @classmethod
    def browse(cls, ids):
        """Mengambil record berdasarkan ID (Operasi READ)."""
        if not isinstance(ids, list):
            ids = [ids] # Ubah ID tunggal menjadi list
            
        conn = Database.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        query = f"SELECT * FROM {cls._table} WHERE id IN %s"
        cursor.execute(query, (tuple(ids),))
        results = cursor.fetchall()
        cursor.close()
        
        records = [cls(cls, record['id'], dict(record)) for record in results]
        return records

# ==================================================================================================
# AREA LATIHAN (ANDA BISA MENGUBAH BAGIAN DI BAWAH INI)
# ==================================================================================================

@registry.register
class Product(Model):
    """Definisi Model untuk Produk."""
    _name = 'product.product'
    
    name = Char(string="Nama Produk")
    price = Float(string="Harga")
    category = Char(string="Kategori")

def run_reading_exercise():
    """Fungsi untuk menjalankan latihan membaca dan mencari data."""
    
    # Inisialisasi semua model yang terdaftar
    for model_cls in registry.values():
        model_cls._init_model()

    # --- PERSIAPAN DATA ---
    # Kita buat beberapa data produk terlebih dahulu agar ada yang bisa dicari.
    # (Jalankan sekali, lalu bisa di-comment agar tidak membuat data duplikat)
    print("\n--- 1. Membuat Data Awal ---")
    Product.create({'name': 'Laptop Pro 15', 'price': 2500.50, 'category': 'Electronics'})
    Product.create({'name': 'Mouse Wireless', 'price': 150.00, 'category': 'Electronics'})
    Product.create({'name': 'Keyboard Mechanical', 'price': 300.75, 'category': 'Electronics'})
    Product.create({'name': 'Buku Python Lanjutan', 'price': 120.00, 'category': 'Books'})
    Product.create({'name': 'Meja Kantor', 'price': 1800.00, 'category': 'Furniture'})
    
    # --- LATIHAN 1: SEARCH - Mencari Semua Produk ---
    print("\n--- 2. Mencari SEMUA produk ---")
    # Domain kosong `[]` artinya "tidak ada filter", jadi ambil semua.
    all_products = Product.search([])
    print(f"Ditemukan {len(all_products)} produk.")
    for product in all_products:
        # `product` adalah sebuah instance dari class Product
        print(f"  - ID: {product.id}, Nama: {product.name}, Harga: {product.price}")

    # --- LATIHAN 2: SEARCH - Mencari dengan Satu Kriteria ---
    print("\n--- 3. Mencari produk dalam kategori 'Electronics' ---")
    # Domain `[('field', 'operator', 'value')]`
    electronic_products = Product.search([('category', '=', 'Electronics')])
    print(f"Ditemukan {len(electronic_products)} produk elektronik.")
    for product in electronic_products:
        print(f"  - ID: {product.id}, Nama: {product.name}")

    # --- LATIHAN 3: SEARCH - Mencari dengan Kriteria Angka ---
    print("\n--- 4. Mencari produk dengan harga di atas 1000 ---")
    expensive_products = Product.search([('price', '>', 1000)])
    print(f"Ditemukan {len(expensive_products)} produk mahal.")
    for product in expensive_products:
        print(f"  - ID: {product.id}, Nama: {product.name}, Harga: {product.price}")

    # --- LATIHAN 4: SEARCH - Mencari dengan Dua Kriteria (AND) ---
    print("\n--- 5. Mencari produk 'Electronics' dengan harga di bawah 500 ---")
    # Jika ada lebih dari satu tuple di domain, Odoo akan menggabungkannya dengan logika AND
    cheap_electronics = Product.search([
        ('category', '=', 'Electronics'),
        ('price', '<', 500)
    ])
    print(f"Ditemukan {len(cheap_electronics)} produk elektronik terjangkau.")
    for product in cheap_electronics:
        print(f"  - ID: {product.id}, Nama: {product.name}, Harga: {product.price}")

    # --- LATIHAN 5: BROWSE - Mengambil Produk Berdasarkan ID ---
    print("\n--- 6. Mengambil produk dengan ID 1 dan 4 ---")
    # `browse` sangat efisien jika kita sudah tahu ID record yang kita mau.
    specific_products = Product.browse([1, 4])
    print(f"Berhasil mengambil {len(specific_products)} produk secara spesifik.")
    for product in specific_products:
        print(f"  - ID: {product.id}, Nama: {product.name}, Kategori: {product.category}")


if __name__ == "__main__":
    print("Memulai Latihan Membaca & Mencari Data (Read/Search)...")
    run_reading_exercise()
    print("\nLatihan selesai.")
