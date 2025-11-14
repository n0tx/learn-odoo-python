# -*- coding: utf-8 -*-
import psycopg2
import psycopg2.extras

# ==================================================================================================
# SIMULASI ODOO ORM FRAMEWORK (BAGIAN INI JANGAN DIUBAH)
# ==================================================================================================
# Framework diperbarui untuk mendukung field Many2one.

class Database:
    _connection = None
    @classmethod
    def get_connection(cls):
        if cls._connection is None:
            try:
                cls._connection = psycopg2.connect(
                    dbname="postgres", user="odoo", password="odoo", host="odoo-db", port="5432"
                )
            except psycopg2.OperationalError as e:
                print(f"Gagal terhubung ke database: {e}")
                exit()
        return cls._connection

class Registry(dict):
    def __init__(self):
        super().__init__()
    def register(self, cls):
        self[cls._name] = cls
        return cls

registry = Registry()

class Field:
    def __init__(self, string=""):
        self.string = string

class Char(Field): pass
class Float(Field): pass

class Many2one(Field):
    """Field untuk relasi Many2one (foreign key)."""
    def __init__(self, comodel_name, string=""):
        super().__init__(string)
        self.comodel_name = comodel_name

class Model:
    _name = None
    _table = None
    _fields = None

    def __init__(self, env, record_id=None, values=None):
        self.env = env
        self.id = record_id
        if values:
            for key, value in values.items():
                setattr(self, key, value)

    @classmethod
    def _init_model(cls):
        cls._table = cls._name.replace('.', '_')
        cls._fields = {name: field for name, field in cls.__dict__.items() if isinstance(field, Field)}
        cls._create_table()

    @classmethod
    def _create_table(cls):
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        columns = ["id SERIAL PRIMARY KEY"]
        for name, field in cls._fields.items():
            col_type = "VARCHAR(255)" # Default
            if isinstance(field, Char):
                col_type = "VARCHAR(255)"
            elif isinstance(field, Float):
                col_type = "FLOAT"
            elif isinstance(field, Many2one):
                # Kolom Many2one disimpan sebagai integer yang mereferensikan ID tabel lain
                col_type = "INTEGER"
            columns.append(f"{name} {col_type}")
        
        query = f"CREATE TABLE IF NOT EXISTS {cls._table} ({', '.join(columns)})"
        cursor.execute(query)
        conn.commit()
        cursor.close()

    @classmethod
    def create(cls, values):
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        columns = [name for name in values if name in cls._fields]
        placeholders = ["%s"] * len(columns)
        data = [values[col] for col in columns]
        
        query = f"INSERT INTO {cls._table} ({', '.join(columns)}) VALUES ({', '.join(placeholders)}) RETURNING id"
        cursor.execute(query, tuple(data))
        new_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        
        print(f"Record baru dibuat di '{cls._name}' dengan ID: {new_id}")
        return cls(cls, new_id, values)

    @classmethod
    def search(cls, domain):
        conn = Database.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        query = f"SELECT * FROM {cls._table}"
        if domain:
            where_clauses = [f"{field} {op} %s" for field, op, val in domain]
            params = [val for field, op, val in domain]
            query += " WHERE " + " AND ".join(where_clauses)
            cursor.execute(query, tuple(params))
        else:
            cursor.execute(query)
            
        results = cursor.fetchall()
        cursor.close()
        return [cls(cls, record['id'], dict(record)) for record in results]

    @classmethod
    def browse(cls, ids):
        if not isinstance(ids, list): ids = [ids]
        conn = Database.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query = f"SELECT * FROM {cls._table} WHERE id IN %s"
        cursor.execute(query, (tuple(ids),))
        results = cursor.fetchall()
        cursor.close()
        return [cls(cls, record['id'], dict(record)) for record in results]

    def write(self, values):
        conn = Database.get_connection()
        cursor = conn.cursor()
        set_clauses = [f"{name} = %s" for name in values if name in self._fields]
        data = [val for name, val in values.items() if name in self._fields]
        data.append(self.id)
        query = f"UPDATE {self._table} SET {', '.join(set_clauses)} WHERE id = %s"
        cursor.execute(query, tuple(data))
        conn.commit()
        cursor.close()
        for key, value in values.items(): setattr(self, key, value)
        return True

    def unlink(self):
        conn = Database.get_connection()
        cursor = conn.cursor()
        query = f"DELETE FROM {self._table} WHERE id = %s"
        cursor.execute(query, (self.id,))
        conn.commit()
        cursor.close()
        return True

# ==================================================================================================
# AREA LATIHAN (ANDA BISA MENGUBAH BAGIAN DI BAWAH INI)
# ==================================================================================================

@registry.register
class ProductCategory(Model):
    """Model untuk Kategori Produk."""
    _name = 'product.category'
    name = Char(string="Nama Kategori")

@registry.register
class Product(Model):
    """Model Produk, sekarang dengan relasi ke Kategori."""
    _name = 'product.product'
    name = Char(string="Nama Produk")
    price = Float(string="Harga")
    # Ini adalah field relasi. Banyak produk bisa memiliki satu kategori.
    # Di database, ini akan menjadi kolom integer bernama 'category_id'.
    category_id = Many2one('product.category', string="Kategori Produk")

def setup_initial_data():
    """Reset dan buat data awal untuk latihan."""
    conn = Database.get_connection()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS product_product, product_category")
    conn.commit()
    cursor.close()
    
    # Inisialisasi ulang model untuk membuat tabel baru
    for model_cls in registry.values():
        model_cls._init_model()

    print("\n--- 1. Membuat Data Kategori ---")
    cat_electronics = ProductCategory.create({'name': 'Electronics'})
    cat_books = ProductCategory.create({'name': 'Books'})

    print("\n--- 2. Membuat Data Produk yang Terhubung ke Kategori ---")
    # Saat membuat produk, kita berikan ID dari kategori yang relevan.
    Product.create({'name': 'Laptop Pro 15', 'price': 2500.50, 'category_id': cat_electronics.id})
    Product.create({'name': 'Mouse Wireless', 'price': 150.00, 'category_id': cat_electronics.id})
    Product.create({'name': 'Buku Python Lanjutan', 'price': 120.00, 'category_id': cat_books.id})

def run_relational_exercise():
    """Fungsi untuk menjalankan latihan relasi Many2one."""
    setup_initial_data()

    # --- LATIHAN 1: Mencari Produk Berdasarkan Kategori ---
    print("\n--- 3. Mencari semua produk dalam kategori 'Electronics' ---")
    
    # Pertama, kita perlu ID dari kategori 'Electronics'
    cat_electronics_list = ProductCategory.search([('name', '=', 'Electronics')])
    if cat_electronics_list:
        cat_electronics_id = cat_electronics_list[0].id
        print(f"ID Kategori 'Electronics' adalah: {cat_electronics_id}")
        
        # Sekarang, cari produk dengan category_id yang cocok
        electronic_products = Product.search([('category_id', '=', cat_electronics_id)])
        
        print(f"Ditemukan {len(electronic_products)} produk elektronik:")
        for product in electronic_products:
            print(f"  - Nama: {product.name}")

    # --- LATIHAN 2: Mengakses Data dari Relasi ---
    print("\n--- 4. Mengambil satu produk dan melihat nama kategorinya ---")
    book_product = Product.search([('name', '=', 'Buku Python Lanjutan')])[0]
    
    # Di simulasi kita, `category_id` hanya menyimpan ID-nya.
    book_category_id = book_product.category_id
    print(f"Produk '{book_product.name}' memiliki category_id: {book_category_id}")
    
    # Untuk mendapatkan nama kategorinya, kita perlu `browse` model ProductCategory
    # Di Odoo asli, ini terjadi secara otomatis (lazy loading).
    book_category = ProductCategory.browse(book_category_id)[0]
    print(f"  -> Nama kategori dari ID {book_category_id} adalah: '{book_category.name}'")


if __name__ == "__main__":
    print("Memulai Latihan Relasi Many2one...")
    run_relational_exercise()
    print("\nLatihan selesai.")
