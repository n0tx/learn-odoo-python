# -*- coding: utf-8 -*-
import psycopg2
import psycopg2.extras

# ==================================================================================================
# SIMULASI ODOO ORM FRAMEWORK (BAGIAN INI JANGAN DIUBAH)
# ==================================================================================================
# Framework diperbarui untuk mendukung field One2many.

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
    def __init__(self, comodel_name, string=""):
        super().__init__(string)
        self.comodel_name = comodel_name

class One2many(Field):
    """Field virtual untuk relasi One2many."""
    def __init__(self, comodel_name, inverse_name, string=""):
        super().__init__(string)
        self.comodel_name = comodel_name
        self.inverse_name = inverse_name # Nama field Many2one di model lain

class Model:
    _name = None
    _table = None
    _fields = None

    def __init__(self, env, record_id=None, values=None):
        self.env = env
        self.id = record_id
        if values:
            for key, value in values.items():
                # Jangan set One2many field sebagai atribut biasa
                if not isinstance(self._fields.get(key), One2many):
                    setattr(self, key, value)

    def __getattribute__(self, name):
        """Override untuk menangani pemanggilan field One2many."""
        # Dapatkan _fields dari class. Gunakan super() untuk menghindari rekursi.
        # Cek juga apakah _fields sudah diinisialisasi untuk menghindari error awal.
        try:
            _fields = super().__getattribute__('_fields')
        except AttributeError:
            _fields = None

        # Cek apakah 'name' adalah field One2many
        if _fields and name in _fields and isinstance(_fields[name], One2many):
            field = _fields[name]
            comodel = registry[field.comodel_name]
            record_id = super().__getattribute__('id')
            
            # Lakukan search di comodel menggunakan inverse_name
            return comodel.search([(field.inverse_name, '=', record_id)])
        
        # Jika bukan field One2many, lanjutkan dengan perilaku default.
        return super().__getattribute__(name)

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
            # Field One2many tidak membuat kolom di database
            if isinstance(field, One2many):
                continue

            col_type = "VARCHAR(255)"
            if isinstance(field, Char): col_type = "VARCHAR(255)"
            elif isinstance(field, Float): col_type = "FLOAT"
            elif isinstance(field, Many2one): col_type = "INTEGER"
            columns.append(f"{name} {col_type}")
        
        query = f"CREATE TABLE IF NOT EXISTS {cls._table} ({', '.join(columns)})"
        cursor.execute(query)
        conn.commit()
        cursor.close()

    @classmethod
    def create(cls, values):
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        columns = [name for name, field in cls._fields.items() if name in values and not isinstance(field, One2many)]
        placeholders = ["%s"] * len(columns)
        data = [values[col] for col in columns]
        
        query = f"INSERT INTO {cls._table} ({', '.join(columns)}) VALUES ({', '.join(placeholders)}) RETURNING id"
        cursor.execute(query, tuple(data))
        new_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        
        return cls(cls, new_id, values)

    @classmethod
    def search(cls, domain):
        conn = Database.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        query = f"SELECT * FROM {cls._table}"
        params = []
        if domain:
            where_clauses = [f"{field} {op} %s" for field, op, val in domain]
            params = [val for field, op, val in domain]
            query += " WHERE " + " AND ".join(where_clauses)
        
        cursor.execute(query, tuple(params))
        results = cursor.fetchall()
        cursor.close()
        return [cls(cls, record['id'], dict(record)) for record in results]

    @classmethod
    def browse(cls, ids):
        if not isinstance(ids, list): ids = [ids]
        if not ids: return []
        conn = Database.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query = f"SELECT * FROM {cls._table} WHERE id IN %s"
        cursor.execute(query, (tuple(ids),))
        results = cursor.fetchall()
        cursor.close()
        return [cls(cls, record['id'], dict(record)) for record in results]

# ==================================================================================================
# AREA LATIHAN (ANDA BISA MENGUBAH BAGIAN DI BAWAH INI)
# ==================================================================================================

@registry.register
class ProductCategory(Model):
    """Model Kategori, sekarang dengan relasi One2many ke Produk."""
    _name = 'product.category'
    name = Char(string="Nama Kategori")
    
    # Ini adalah field relasi One2many. Satu kategori bisa memiliki banyak produk.
    # 'product.product' adalah model tujuan.
    # 'category_id' adalah field Many2one di model tujuan yang menjadi penghubung.
    product_ids = One2many('product.product', 'category_id', string="Produk")

@registry.register
class Product(Model):
    """Model Produk, tidak berubah dari latihan sebelumnya."""
    _name = 'product.product'
    name = Char(string="Nama Produk")
    price = Float(string="Harga")
    category_id = Many2one('product.category', string="Kategori Produk")

def setup_initial_data():
    """Reset dan buat data awal untuk latihan."""
    conn = Database.get_connection()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS product_product, product_category")
    conn.commit()
    cursor.close()
    
    for model_cls in registry.values():
        model_cls._init_model()

    print("\n--- 1. Membuat Data Awal (Sama seperti sebelumnya) ---")
    cat_electronics = ProductCategory.create({'name': 'Electronics'})
    cat_books = ProductCategory.create({'name': 'Books'})
    Product.create({'name': 'Laptop Pro 15', 'price': 2500.50, 'category_id': cat_electronics.id})
    Product.create({'name': 'Mouse Wireless', 'price': 150.00, 'category_id': cat_electronics.id})
    Product.create({'name': 'Buku Python Lanjutan', 'price': 120.00, 'category_id': cat_books.id})

def run_relational_exercise():
    """Fungsi untuk menjalankan latihan relasi One2many."""
    setup_initial_data()

    # --- LATIHAN: Mengakses Record Anak dari Induk ---
    print("\n--- 2. Mengambil kategori 'Electronics' dan menampilkan produk di dalamnya ---")
    
    # Langkah 1: Cari record induk (kategori)
    cat_electronics_list = ProductCategory.search([('name', '=', 'Electronics')])
    if cat_electronics_list:
        cat_electronics = cat_electronics_list[0]
        print(f"Ditemukan kategori: '{cat_electronics.name}' (ID: {cat_electronics.id})")
        
        # Langkah 2: Akses field One2many-nya
        # Di balik layar, ini akan menjalankan: Product.search([('category_id', '=', cat_electronics.id)])
        products_in_category = cat_electronics.product_ids
        
        print(f"  -> Terdapat {len(products_in_category)} produk dalam kategori ini:")
        
        # Langkah 3: Lakukan iterasi pada hasilnya
        for product in products_in_category:
            print(f"     - Nama: {product.name}, Harga: {product.price}")

if __name__ == "__main__":
    print("Memulai Latihan Relasi One2many...")
    run_relational_exercise()
    print("\nLatihan selesai.")
