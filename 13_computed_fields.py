# -*- coding: utf-8 -*-
import psycopg2
import psycopg2.extras

# =================================================================================================
# SIMULASI ODOO ORM FRAMEWORK (BAGIAN INI JANGAN DIUBAH)
# =================================================================================================
# Framework diperbarui untuk mendukung:
# 1. Computed Fields: Field yang nilainya dihitung oleh method Python.
# 2. Simulasi decorator @api.depends melalui parameter 'compute'.
# 3. Penambahan field Float untuk kalkulasi.

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
    def __init__(self, string="", compute=None):
        self.string = string
        self.compute = compute # Nama method compute, misal: '_compute_total'

class Char(Field): pass
class Float(Field): pass

class Model:
    _name = None
    _table = None
    _fields = None

    def __init__(self, env, record_id=None, values=None):
        self.env = env
        self.id = record_id
        # Inisialisasi cache untuk computed fields
        self._cache = {}
        if values:
            for key, value in values.items():
                setattr(self, key, value)

    def __getattribute__(self, name):
        """
        Override untuk menangani pemanggilan computed field.
        """
        # Gunakan super() untuk mengakses atribut instance secara langsung dan menghindari rekursi.
        _fields = super().__getattribute__('_fields')
        _cache = super().__getattribute__('_cache')

        # Cek apakah field yang diakses adalah computed field.
        if _fields and name in _fields and _fields[name].compute:
            # Jika nilai belum ada di cache, maka hitung.
            if name not in _cache:
                print(f"COMPUTE: Menghitung nilai untuk field '{name}' menggunakan method '{_fields[name].compute}'...")
                compute_method = getattr(self, _fields[name].compute)
                # Panggil method compute, yang akan mengisi cache.
                compute_method()
            
            # Kembalikan nilai langsung dari cache untuk menghentikan rekursi.
            return _cache[name]

        # Untuk field biasa, gunakan perilaku default.
        return super().__getattribute__(name)

    @classmethod
    def create(cls, values):
        # Filter out computed fields from values before inserting to DB
        non_computed_values = {}
        for key, value in values.items():
            if not cls._fields[key].compute:
                non_computed_values[key] = value

        field_names = non_computed_values.keys()
        column_names = ', '.join(field_names)
        field_placeholders = ', '.join(['%s'] * len(field_names))
        
        query = f"INSERT INTO {cls._table} ({column_names}) VALUES ({field_placeholders}) RETURNING id"
        
        conn = cls.env.cr.connection
        cls.env.cr.execute(query, list(non_computed_values.values()))
        new_id = cls.env.cr.fetchone()[0]
        conn.commit()
        
        print(f"SUCCESS: Record '{cls._name}' baru dibuat dengan ID: {new_id}")
        return cls.browse(new_id)

    @classmethod
    def browse(cls, ids):
        if not ids: return []
        is_single_id = not isinstance(ids, list)
        record_ids = [ids] if is_single_id else ids
        if not record_ids: return []

        query = f"SELECT * FROM {cls._table} WHERE id IN %s"
        cls.env.cr.execute(query, (tuple(record_ids),))
        records_data = cls.env.cr.fetchall()
        
        colnames = [desc[0] for desc in cls.env.cr.description]
        results = []
        for data in records_data:
            values = dict(zip(colnames, data))
            record_id = values.pop('id')
            instance = cls(cls.env, record_id, values)
            results.append(instance)
        
        if is_single_id: return results[0] if results else None
        return results

    @classmethod
    def _init_table(cls):
        conn = cls.env.cr.connection
        
        field_definitions = ["id SERIAL PRIMARY KEY"]
        for name, field in cls._fields.items():
            # Computed fields tidak dibuatkan kolom di database (secara default)
            if field.compute:
                continue
            
            if isinstance(field, Char):
                field_definitions.append(f"{name} VARCHAR(255)")
            elif isinstance(field, Float):
                field_definitions.append(f"{name} REAL") # Tipe data REAL atau DOUBLE PRECISION untuk float

        query = f"CREATE TABLE IF NOT EXISTS {cls._table} ({', '.join(field_definitions)})"
        cls.env.cr.execute(query)
        conn.commit()
        print(f"Table '{cls._table}' is ready.")

class Environment:
    def __init__(self, cursor):
        self.cr = cursor
        self.registry = registry

    def __getitem__(self, model_name):
        ModelClass = self.registry.get(model_name)
        if not ModelClass:
            raise KeyError(f"Model '{model_name}' not found in registry.")
        ModelClass.env = self
        return ModelClass

# =================================================================================================
# CONTOH IMPLEMENTASI MODEL (BAGIAN INI YANG ANDA UBAH)
# =================================================================================================

@registry.register
class SaleOrderLine(Model):
    _name = 'sale.order.line'
    _table = 'sale_order_line'
    _fields = {
        'product_name': Char(string='Product'),
        'quantity': Float(string='Quantity'),
        'price_unit': Float(string='Unit Price'),
        'price_subtotal': Float(string='Subtotal', compute='_compute_price_subtotal'),
    }

    def _compute_price_subtotal(self):
        """
        Method yang menghitung nilai untuk field 'price_subtotal'.
        Di Odoo asli, ini akan bekerja pada seluruh recordset (self).
        Di simulasi ini, kita sederhanakan untuk satu record.
        """
        print(f"-> Menjalankan _compute_price_subtotal untuk record ID {self.id}...")
        # 1. Hitung nilai dan simpan di variabel lokal untuk menghindari rekursi.
        subtotal = self.quantity * self.price_unit
        
        # 2. Gunakan variabel lokal untuk mencetak hasil.
        print(f"-> Hasil: {self.quantity} * {self.price_unit} = {subtotal}")

        # 3. Set nilai ke field pada instance.
        self.price_subtotal = subtotal
        
        # 4. Simpan di cache untuk menghindari perhitungan ulang yang tidak perlu.
        self._cache['price_subtotal'] = subtotal


def run_computed_fields_example():
    """
    Fungsi untuk menjalankan contoh penggunaan Computed Fields.
    """
    conn = Database.get_connection()
    cr = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    env = Environment(cr)

    # Inisialisasi tabel
    OrderLineModel = env['sale.order.line']
    OrderLineModel._init_table()

    # 1. Buat baris pesanan baru.
    print("\n--- 1. Membuat Order Line Baru ---")
    line = OrderLineModel.create({
        'product_name': 'Laptop Super Canggih',
        'quantity': 2,
        'price_unit': 1500.50,
    })
    print(f"Data tersimpan: Product={line.product_name}, Qty={line.quantity}, Price={line.price_unit}")

    # 2. Akses computed field. Ini akan memicu method compute-nya.
    print("\n--- 2. Mengakses Computed Field ---")
    # Saat kita mencoba mengakses 'line.price_subtotal', method __getattribute__ akan
    # mendeteksi bahwa ini adalah computed field dan memanggil '_compute_price_subtotal'.
    subtotal = line.price_subtotal
    print(f"HASIL: Subtotal yang dihitung adalah: {subtotal}")

    # 3. Akses field yang sama lagi. Seharusnya tidak ada perhitungan ulang.
    # (Simulasi sederhana ini akan menghitung ulang, Odoo asli lebih canggih)
    print("\n--- 3. Mengakses Ulang Computed Field ---")
    subtotal_again = line.price_subtotal
    print(f"HASIL: Subtotal (diakses lagi) adalah: {subtotal_again}")
    print("(CATATAN: Dalam simulasi ini, method compute tetap dipanggil. Odoo asli memiliki cache yang lebih cerdas.)")


    cr.close()

if __name__ == "__main__":
    run_computed_fields_example()
