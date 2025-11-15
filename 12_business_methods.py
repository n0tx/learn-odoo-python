# -*- coding: utf-8 -*-
import psycopg2
import psycopg2.extras

# =================================================================================================
# SIMULASI ODOO ORM FRAMEWORK (BAGIAN INI JANGAN DIUBAH)
# =================================================================================================
# Framework diperbarui untuk mendukung:
# 1. Penambahan 'write' method untuk memodifikasi record.
# 2. Penambahan 'state' field (Selection) untuk workflow.
# 3. Kemampuan memanggil method custom pada instance model.

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
class Selection(Field):
    def __init__(self, selection, string=""):
        super().__init__(string)
        self.selection = selection # List of tuples, e.g., [('draft', 'Draft'), ('done', 'Done')]

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
    def create(cls, values):
        field_names = values.keys()
        column_names = ', '.join(field_names)
        field_placeholders = ', '.join(['%s'] * len(field_names))
        
        query = f"INSERT INTO {cls._table} ({column_names}) VALUES ({field_placeholders}) RETURNING id"
        
        conn = cls.env.cr.connection
        cls.env.cr.execute(query, list(values.values()))
        new_id = cls.env.cr.fetchone()[0]
        conn.commit()
        
        print(f"SUCCESS: Record '{cls._name}' baru dibuat dengan ID: {new_id}")
        return cls.browse(new_id)

    def write(self, values):
        """
        Method untuk mengupdate record yang ada.
        """
        if not self.id:
            print("ERROR: Tidak bisa melakukan write pada record tanpa ID.")
            return False

        field_names = values.keys()
        set_clauses = ', '.join([f"{key} = %s" for key in field_names])
        
        query = f"UPDATE {self._table} SET {set_clauses} WHERE id = %s"
        
        conn = self.env.cr.connection
        # Urutan values harus sesuai dengan urutan field_names, ditambah self.id di akhir
        query_params = list(values.values()) + [self.id]
        self.env.cr.execute(query, query_params)
        conn.commit()

        # Perbarui nilai pada instance object saat ini
        for key, value in values.items():
            setattr(self, key, value)

        print(f"SUCCESS: Record '{self._name}' dengan ID {self.id} telah diupdate.")
        return True

    @classmethod
    def search(cls, domain):
        if not domain:
            query = f"SELECT id FROM {cls._table}"
            cls.env.cr.execute(query)
        else:
            field, op, value = domain[0]
            query = f"SELECT id FROM {cls._table} WHERE {field} {op} %s"
            cls.env.cr.execute(query, (value,))
            
        record_ids = [row[0] for row in cls.env.cr.fetchall()]
        return cls.browse(record_ids)

    @classmethod
    def browse(cls, ids):
        if not ids:
            return []

        is_single_id = not isinstance(ids, list)
        record_ids = [ids] if is_single_id else ids

        if not record_ids:
            return []

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
        
        if is_single_id:
            return results[0] if results else None
        
        return results

    @classmethod
    def _init_table(cls):
        conn = cls.env.cr.connection
        
        field_definitions = ["id SERIAL PRIMARY KEY"]
        for name, field in cls._fields.items():
            if isinstance(field, (Char, Selection)):
                field_definitions.append(f"{name} VARCHAR(255)")

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
class SaleOrder(Model):
    _name = 'sale.order'
    _table = 'sale_order'
    _fields = {
        'name': Char(string='Order Reference'),
        'state': Selection([
            ('draft', 'Quotation'),
            ('sent', 'Quotation Sent'),
            ('sale', 'Sales Order'),
            ('done', 'Locked'),
            ('cancel', 'Cancelled'),
        ], string='Status'),
    }

    # ================== BUSINESS METHODS ==================
    
    def action_confirm(self):
        """
        Ini adalah contoh business method.
        Tujuannya adalah mengubah state dari 'draft' menjadi 'sale' (Sales Order).
        """
        print(f"INFO: Method 'action_confirm' dipanggil untuk order '{self.name}' (ID: {self.id}).")
        if self.state == 'draft':
            print("ACTION: Mengubah status dari 'draft' -> 'sale'.")
            self.write({'state': 'sale'})
        else:
            print(f"WARNING: Aksi tidak valid. Status saat ini adalah '{self.state}', bukan 'draft'.")
        return True

    def action_cancel(self):
        """
        Contoh business method lain untuk membatalkan pesanan.
        """
        print(f"INFO: Method 'action_cancel' dipanggil untuk order '{self.name}' (ID: {self.id}).")
        print("ACTION: Mengubah status menjadi 'cancel'.")
        self.write({'state': 'cancel'})
        return True


def run_business_methods_example():
    """
    Fungsi untuk menjalankan contoh penggunaan Business Methods.
    """
    conn = Database.get_connection()
    cr = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    env = Environment(cr)

    # Inisialisasi tabel
    SaleOrderModel = env['sale.order']
    SaleOrderModel._init_table()

    # 1. Buat Sales Order baru. Secara default, statusnya harus 'draft'.
    print("\n--- 1. Membuat Sales Order Baru ---")
    # Di Odoo asli, nilai default akan menangani ini, tapi di sini kita set manual.
    so = SaleOrderModel.create({
        'name': 'SO/2025/001',
        'state': 'draft',
    })
    print(f"Status awal: {so.state}")

    # 2. Panggil business method untuk mengonfirmasi pesanan.
    print("\n--- 2. Mengonfirmasi Sales Order ---")
    so.action_confirm()
    
    # Kita perlu browse ulang untuk melihat data terbaru dari database
    so_after_confirm = SaleOrderModel.browse(so.id)
    print(f"Status setelah konfirmasi: {so_after_confirm.state}")

    # 3. Coba panggil method yang sama lagi (seharusnya tidak melakukan apa-apa)
    print("\n--- 3. Mencoba Konfirmasi Ulang (Harusnya Gagal) ---")
    so_after_confirm.action_confirm()
    print(f"Status tetap: {so_after_confirm.state}")

    # 4. Panggil business method lain untuk membatalkan pesanan.
    print("\n--- 4. Membatalkan Sales Order ---")
    so_after_confirm.action_cancel()
    so_after_cancel = SaleOrderModel.browse(so.id)
    print(f"Status setelah pembatalan: {so_after_cancel.state}")

    cr.close()

if __name__ == "__main__":
    run_business_methods_example()
