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
    _auto = True

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
        
        return cls(cls, new_id, values)

    @classmethod
    def search(cls, domain):
        """Mencari record berdasarkan kriteria/domain (Operasi READ)."""
        conn = Database.get_connection()
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
        
        records = [cls(cls, record['id'], dict(record)) for record in results]
        return records

    @classmethod
    def browse(cls, ids):
        """Mengambil record berdasarkan ID (Operasi READ)."""
        if not isinstance(ids, list):
            ids = [ids]
            
        conn = Database.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        query = f"SELECT * FROM {cls._table} WHERE id IN %s"
        cursor.execute(query, (tuple(ids),))
        results = cursor.fetchall()
        cursor.close()
        
        records = [cls(cls, record['id'], dict(record)) for record in results]
        return records

    def write(self, values):
        """Memperbarui record yang ada di database (Operasi UPDATE)."""
        conn = Database.get_connection()
        cursor = conn.cursor()

        set_clauses = []
        data = []
        for name, value in values.items():
            if name in self._fields:
                set_clauses.append(f"{name} = %s")
                data.append(value)
        
        if not set_clauses:
            return False

        data.append(self.id)
        query = f"UPDATE {self._table} SET {', '.join(set_clauses)} WHERE id = %s"
        
        cursor.execute(query, tuple(data))
        conn.commit()
        cursor.close()

        for key, value in values.items():
            setattr(self, key, value)
            
        return True

    def unlink(self):
        """Menghapus record dari database (Operasi DELETE)."""
        conn = Database.get_connection()
        cursor = conn.cursor()

        query = f"DELETE FROM {self._table} WHERE id = %s"
        cursor.execute(query, (self.id,))
        
        conn.commit()
        cursor.close()
        
        print(f"Record ID {self.id} dari '{self._name}' telah dihapus.")
        return True

# = an=================================================================================================
# AREA LATIHAN (ANDA BISA MENGUBAH BAGIAN DI BAWAH INI)
# ==================================================================================================

@registry.register
class Product(Model):
    """Definisi Model untuk Produk."""
    _name = 'product.product'
    
    name = Char(string="Nama Produk")
    price = Float(string="Harga")
    category = Char(string="Kategori")

def setup_initial_data():
    """Membuat data awal jika tabel kosong."""
    if not Product.search([]):
        print("Tabel produk kosong, membuat data awal...")
        Product.create({'name': 'Laptop Pro 15', 'price': 2500.50, 'category': 'Electronics'})
        Product.create({'name': 'Mouse Wireless', 'price': 150.00, 'category': 'Electronics'})
        Product.create({'name': 'Buku Python Lanjutan', 'price': 120.00, 'category': 'Books'})
        Product.create({'name': 'Produk Untuk Dihapus', 'price': 10.00, 'category': 'Temporary'})
    else:
        print("Data produk sudah ada.")

def run_deleting_exercise():
    """Fungsi untuk menjalankan latihan menghapus data."""
    
    # Inisialisasi semua model yang terdaftar
    for model_cls in registry.values():
        model_cls._init_model()

    # Persiapan data
    setup_initial_data()

    # --- LATIHAN: Menghapus Satu Produk ---
    print("\n--- 1. Menghapus produk dengan nama 'Produk Untuk Dihapus' ---")
    
    # Langkah 1: Cari produknya
    products_to_delete = Product.search([('name', '=', 'Produk Untuk Dihapus')])
    
    if products_to_delete:
        product_to_delete = products_to_delete[0]
        print(f"Ditemukan produk untuk dihapus: ID {product_to_delete.id}, Nama: {product_to_delete.name}")
        
        # Langkah 2: Panggil metode unlink() pada record tersebut
        product_to_delete.unlink()
        
        # Langkah 3 (Verifikasi): Coba cari lagi produk tersebut
        print("Mencari kembali produk yang sudah dihapus...")
        remaining_products = Product.search([('name', '=', 'Produk Untuk Dihapus')])
        
        if not remaining_products:
            print("Verifikasi BERHASIL: Produk tidak lagi ditemukan di database.")
        else:
            print("Verifikasi GAGAL: Produk masih ada di database.")
            
    else:
        print("Produk 'Produk Untuk Dihapus' tidak ditemukan (mungkin sudah dihapus).")

    # --- Verifikasi Data Tersisa ---
    print("\n--- 2. Menampilkan semua produk yang tersisa ---")
    all_products = Product.search([])
    print(f"Jumlah produk yang tersisa di database: {len(all_products)}")
    for p in all_products:
        print(f"  - ID: {p.id}, Nama: {p.name}")


if __name__ == "__main__":
    print("Memulai Latihan Menghapus Data (Delete/Unlink)...")
    run_deleting_exercise()
    print("\nLatihan selesai.")
