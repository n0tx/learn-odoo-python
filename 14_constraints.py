# -*- coding: utf-8 -*-
import psycopg2
import psycopg2.extras

# =================================================================================================
# SIMULASI ODOO ORM FRAMEWORK (BAGIAN INI JANGAN DIUBAH)
# =================================================================================================
# Framework diperbarui untuk mendukung:
# 1. Constraints: Aturan validasi data yang dijalankan saat create/write.
# 2. Simulasi decorator @api.constrains melalui atribut '_constraints'.
# 3. Custom exception 'ValidationError' untuk menghentikan transaksi.
# 4. Penanganan transaksi (rollback) saat validasi gagal.

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

class ValidationError(Exception):
    """Custom exception untuk validation errors, mirip dengan odoo.exceptions.ValidationError."""
    pass

class Field:
    def __init__(self, string=""):
        self.string = string

class Char(Field): pass
class Float(Field): pass

class Model:
    _name = None
    _table = None
    _fields = None
    _constraints = [] # Daftar constraint, e.g., [('_check_prices', ['sale_price', 'cost_price'])]

    def __init__(self, env, record_id=None, values=None):
        self.env = env
        self.id = record_id
        if values:
            for key, value in values.items():
                setattr(self, key, value)

    def _execute_constraints(self, updated_fields=None):
        """Memicu method constraint jika field yang relevan diubah."""
        if not updated_fields:
            return
        
        for method_name, constrained_fields in self._constraints:
            # Cek apakah ada irisan antara field yang diupdate dan field yang memicu constraint
            if any(field in updated_fields for field in constrained_fields):
                print(f"CONSTRAINT: Menjalankan constraint '{method_name}'...")
                constraint_method = getattr(self, method_name)
                constraint_method()

    @classmethod
    def create(cls, values):
        conn = cls.env.cr.connection
        try:
            field_names = values.keys()
            column_names = ', '.join(field_names)
            field_placeholders = ', '.join(['%s'] * len(field_names))
            
            query = f"INSERT INTO {cls._table} ({column_names}) VALUES ({field_placeholders}) RETURNING id"
            
            cls.env.cr.execute(query, list(values.values()))
            new_id = cls.env.cr.fetchone()[0]
            
            # Buat instance baru untuk menjalankan constraint
            new_record = cls.browse(new_id)
            new_record._execute_constraints(values.keys())

            conn.commit()
            print(f"SUCCESS: Record '{cls._name}' baru dibuat dengan ID: {new_id}")
            return new_record
        except ValidationError as e:
            print(f"ERROR: Validasi gagal! Pesan: {e}")
            conn.rollback() # Batalkan transaksi jika ada error validasi
            return None
        except Exception as e:
            print(f"ERROR: Terjadi kesalahan database: {e}")
            conn.rollback()
            return None

    def write(self, values):
        conn = self.env.cr.connection
        try:
            field_names = values.keys()
            set_clauses = ', '.join([f"{key} = %s" for key in field_names])
            
            query = f"UPDATE {self._table} SET {set_clauses} WHERE id = %s"
            
            query_params = list(values.values()) + [self.id]
            self.env.cr.execute(query, query_params)

            # Perbarui nilai pada instance dan jalankan constraint
            for key, value in values.items():
                setattr(self, key, value)
            self._execute_constraints(values.keys())

            conn.commit()
            print(f"SUCCESS: Record '{self._name}' dengan ID {self.id} telah diupdate.")
            return True
        except ValidationError as e:
            print(f"ERROR: Validasi gagal! Pesan: {e}")
            conn.rollback()
            return False
        except Exception as e:
            print(f"ERROR: Terjadi kesalahan database: {e}")
            conn.rollback()
            return False

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
            if isinstance(field, Char):
                field_definitions.append(f"{name} VARCHAR(255)")
            elif isinstance(field, Float):
                field_definitions.append(f"{name} REAL")

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
class ProductTemplate(Model):
    _name = 'product.template'
    _table = 'product_template'
    _fields = {
        'name': Char(string='Product Name'),
        'cost_price': Float(string='Cost Price'),
        'sale_price': Float(string='Sale Price'),
    }
    
    # Simulasi decorator @api.constrains('sale_price', 'cost_price')
    _constraints = [
        ('_check_prices', ['sale_price', 'cost_price'])
    ]

    def _check_prices(self):
        """
        Constraint method untuk memastikan harga jual tidak lebih rendah dari harga modal.
        """
        if self.sale_price < self.cost_price:
            # Raise ValidationError untuk menghentikan operasi dan memberikan pesan error.
            raise ValidationError("Harga Jual (Sale Price) tidak boleh lebih rendah dari Harga Modal (Cost Price).")
        print("-> Validasi harga berhasil.")


def run_constraints_example():
    """
    Fungsi untuk menjalankan contoh penggunaan Constraints.
    """
    conn = Database.get_connection()
    cr = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    env = Environment(cr)

    # Hapus tabel lama jika ada untuk memastikan skema terbaru yang digunakan
    cr.execute("DROP TABLE IF EXISTS product_template CASCADE;")
    print("INFO: Tabel 'product_template' lama (jika ada) telah dihapus.")

    ProductModel = env['product.template']
    ProductModel._init_table()

    # 1. Mencoba membuat produk dengan harga yang VALID
    print("\n--- 1. Membuat Produk (Harga Valid) ---")
    product1 = ProductModel.create({
        'name': 'Laptop Standar',
        'cost_price': 700.0,
        'sale_price': 850.0,
    })
    # Seharusnya berhasil
    assert product1 is not None, "Gagal membuat produk yang seharusnya valid!"

    # 2. Mencoba membuat produk dengan harga yang TIDAK VALID
    print("\n--- 2. Membuat Produk (Harga Tidak Valid) ---")
    product2 = ProductModel.create({
        'name': 'Meja Murah',
        'cost_price': 100.0,
        'sale_price': 90.0, # Harga jual < harga modal
    })
    # Seharusnya gagal dan product2 adalah None
    assert product2 is None, "Berhasil membuat produk yang seharusnya tidak valid!"

    # 3. Mencoba mengupdate produk menjadi TIDAK VALID
    print("\n--- 3. Mengupdate Produk Menjadi Tidak Valid ---")
    print(f"Harga awal '{product1.name}': Jual={product1.sale_price}, Modal={product1.cost_price}")
    success = product1.write({'sale_price': 650.0}) # Harga jual < harga modal
    # Seharusnya gagal dan success adalah False
    assert not success, "Berhasil mengupdate produk menjadi tidak valid!"
    
    # Browse ulang untuk memastikan data tidak berubah di database
    product1_after_fail = ProductModel.browse(product1.id)
    print(f"Harga setelah gagal update: Jual={product1_after_fail.sale_price}, Modal={product1_after_fail.cost_price}")
    assert product1_after_fail.sale_price == 850.0, "Harga produk berubah meskipun update gagal!"

    # 4. Mencoba mengupdate produk menjadi VALID
    print("\n--- 4. Mengupdate Produk Menjadi Valid ---")
    success_update = product1.write({'sale_price': 900.0})
    # Seharusnya berhasil
    assert success_update, "Gagal mengupdate produk yang seharusnya valid!"
    product1_after_success = ProductModel.browse(product1.id)
    print(f"Harga setelah berhasil update: Jual={product1_after_success.sale_price}, Modal={product1_after_success.cost_price}")
    assert product1_after_success.sale_price == 900.0, "Harga produk tidak berubah setelah update berhasil!"

    cr.close()

if __name__ == "__main__":
    run_constraints_example()
