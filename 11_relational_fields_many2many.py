# -*- coding: utf-8 -*-
import psycopg2
import psycopg2.extras

# =================================================================================================
# SIMULASI ODOO ORM FRAMEWORK (BAGIAN INI JANGAN DIUBAH)
# =================================================================================================
# Framework diperbarui untuk mendukung field Many2many.

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
class Integer(Field): pass

class Many2one(Field):
    def __init__(self, comodel_name, string=""):
        super().__init__(string)
        self.comodel_name = comodel_name

class One2many(Field):
    def __init__(self, comodel_name, inverse_name, string=""):
        super().__init__(string)
        self.comodel_name = comodel_name
        self.inverse_name = inverse_name

class Many2many(Field):
    """Field untuk relasi Many2many."""
    def __init__(self, comodel_name, relation=None, column1=None, column2=None, string=""):
        super().__init__(string)
        self.comodel_name = comodel_name
        # Odoo biasanya bisa menebak nama-nama ini, tapi kita definisikan secara eksplisit
        self.relation = relation if relation else f"{Model._table}_{comodel_name.replace('.', '_')}_rel"
        self.column1 = column1 if column1 else f"{Model._table}_id"
        self.column2 = column2 if column2 else f"{comodel_name.replace('.', '_')}_id"

class Model:
    _name = None
    _table = None
    _fields = None

    def __init__(self, env, record_id=None, values=None):
        self.env = env
        self.id = record_id
        if values:
            for key, value in values.items():
                if not isinstance(self._fields.get(key), (One2many, Many2many)):
                    setattr(self, key, value)

    def __getattribute__(self, name):
        try:
            _fields = super().__getattribute__('_fields')
        except AttributeError:
            _fields = None

        if _fields and name in _fields and isinstance(_fields[name], (One2many, Many2many)):
            field = _fields[name]
            Comodel = self.env[field.comodel_name]
            if isinstance(field, One2many):
                return Comodel.search([(field.inverse_name, '=', self.id)])
            elif isinstance(field, Many2many):
                # Query ke tabel relasi untuk mendapatkan ID dari comodel
                query = f"SELECT {field.column2} FROM {field.relation} WHERE {field.column1} = %s"
                self.env.cr.execute(query, (self.id,))
                comodel_ids = [row[0] for row in self.env.cr.fetchall()]
                return Comodel.browse(comodel_ids)
        return super().__getattribute__(name)

    @classmethod
    def create(cls, values):
        # Implementasi create disederhanakan dan tidak menangani M2M secara langsung
        # Di Odoo asli, Anda bisa memberikan daftar command (misal: (6, 0, [ids]))
        print(f"INFO: Method 'create' untuk '{cls._name}' dipanggil dengan values: {values}")
        print("CATATAN: Simulasi ini tidak mengimplementasikan penulisan relasi M2M saat 'create'. Relasi harus dibuat manual setelah record utama ada.")
        
        field_names = [k for k, v in values.items() if not isinstance(cls._fields.get(k), (One2many, Many2many))]
        field_placeholders = ', '.join(['%s'] * len(field_names))
        
        column_names = ', '.join(field_names)
        
        query = f"INSERT INTO {cls._table} ({column_names}) VALUES ({field_placeholders}) RETURNING id"
        
        conn = cls.env.cr.connection
        cls.env.cr.execute(query, [values[k] for k in field_names])
        new_id = cls.env.cr.fetchone()[0]
        conn.commit()
        
        print(f"SUCCESS: Record '{cls._name}' baru dibuat dengan ID: {new_id}")
        return cls.browse(new_id)

    @classmethod
    def search(cls, domain):
        # Implementasi search disederhanakan
        if not domain:
            query = f"SELECT id FROM {cls._table}"
            cls.env.cr.execute(query)
        else:
            # Hanya handle kasus sederhana: [('field', '=', 'value')]
            field, op, value = domain[0]
            query = f"SELECT id FROM {cls._table} WHERE {field} {op} %s"
            cls.env.cr.execute(query, (value,))
            
        record_ids = [row[0] for row in cls.env.cr.fetchall()]
        return cls.browse(record_ids)

    @classmethod
    def browse(cls, ids):
        if not ids:
            return []  # Selalu kembalikan list kosong jika tidak ada ids

        # Cek apakah input aslinya adalah ID tunggal atau list
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
        
        # Jika input asli adalah ID tunggal, kembalikan satu objek (atau None jika tidak ditemukan)
        if is_single_id:
            return results[0] if results else None
        
        # Jika input asli adalah list, selalu kembalikan list
        return results

    @classmethod
    def _init_main_table(cls):
        """Fungsi untuk membuat tabel utama model (tanpa relasi M2M)."""
        conn = cls.env.cr.connection
        
        field_definitions = ["id SERIAL PRIMARY KEY"]
        for name, field in cls._fields.items():
            if isinstance(field, Char):
                field_definitions.append(f"{name} VARCHAR(255)")
            elif isinstance(field, Integer):
                field_definitions.append(f"{name} INTEGER")
            elif isinstance(field, Many2one):
                comodel_table = field.comodel_name.replace('.', '_')
                field_definitions.append(f"{name} INTEGER REFERENCES {comodel_table}(id)")

        query = f"CREATE TABLE IF NOT EXISTS {cls._table} ({', '.join(field_definitions)})"
        cls.env.cr.execute(query)
        print(f"Table '{cls._table}' is ready.")

    @classmethod
    def _init_m2m_relations(cls):
        """Fungsi untuk membuat tabel relasi Many2many."""
        conn = cls.env.cr.connection
        
        for name, field in cls._fields.items():
            if isinstance(field, Many2many):
                comodel = cls.env[field.comodel_name]
                rel_table = field.relation
                col1 = field.column1
                col2 = field.column2
                
                rel_query = f"""
                CREATE TABLE IF NOT EXISTS {rel_table} (
                    {col1} INTEGER REFERENCES {cls._table}(id) ON DELETE CASCADE,
                    {col2} INTEGER REFERENCES {comodel._table}(id) ON DELETE CASCADE,
                    PRIMARY KEY ({col1}, {col2})
                )"""
                cls.env.cr.execute(rel_query)
                print(f"M2M relation table '{rel_table}' is ready.")
        
        conn.commit()

class Environment:
    def __init__(self, cursor):
        self.cr = cursor
        self.registry = registry

    def __getitem__(self, model_name):
        ModelClass = self.registry.get(model_name)
        if not ModelClass:
            raise KeyError(f"Model '{model_name}' not found in registry.")
        
        # Simulasikan cara Odoo memberikan env ke setiap model
        ModelClass.env = self
        return ModelClass

# =================================================================================================
# CONTOH IMPLEMENTASI MODEL (BAGIAN INI YANG ANDA UBAH)
# =================================================================================================

@registry.register
class Student(Model):
    _name = 'res.student'
    _table = 'res_student'
    _fields = {
        'name': Char(string='Student Name'),
        'course_ids': Many2many('res.course', 'res_student_course_rel', 'student_id', 'course_id', string='Courses'),
    }
    # Definisikan nama kolom dan tabel relasi secara eksplisit untuk kejelasan
    _fields['course_ids'].relation = 'res_student_course_rel'
    _fields['course_ids'].column1 = 'student_id'
    _fields['course_ids'].column2 = 'course_id'


@registry.register
class Course(Model):
    _name = 'res.course'
    _table = 'res_course'
    _fields = {
        'name': Char(string='Course Name'),
        'student_ids': Many2many('res.student', 'res_student_course_rel', 'course_id', 'student_id', string='Students'),
    }
    # Pastikan parameter relasi konsisten dengan model Student
    _fields['student_ids'].relation = 'res_student_course_rel'
    _fields['student_ids'].column1 = 'course_id'
    _fields['student_ids'].column2 = 'student_id'


def run_many2many_example():
    """
    Fungsi untuk menjalankan contoh relasi Many2many.
    """
    conn = Database.get_connection()
    cr = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    env = Environment(cr)

    # Tahap 1: Inisialisasi semua tabel utama terlebih dahulu
    print("\n--- Tahap 1: Membuat Tabel Utama ---")
    env['res.student']._init_main_table()
    env['res.course']._init_main_table()
    conn.commit()

    # Tahap 2: Setelah semua tabel utama ada, buat tabel relasi M2M
    print("\n--- Tahap 2: Membuat Tabel Relasi M2M ---")
    env['res.student']._init_m2m_relations()
    # env['res.course']._init_m2m_relations() # Cukup panggil sekali karena tabel relasinya sama
    conn.commit()

    # 1. Buat beberapa data master (Mahasiswa dan Mata Kuliah)
    print("\n--- Membuat Data Awal ---")
    student1 = env['res.student'].create({'name': 'Budi'})
    student2 = env['res.student'].create({'name': 'Ani'})
    course_math = env['res.course'].create({'name': 'Matematika Dasar'})
    course_phys = env['res.course'].create({'name': 'Fisika Dasar'})

    # 2. Membuat relasi Many2many secara manual
    # Di Odoo, ini biasanya dilakukan dengan command (6, 0, [ids]) atau (4, id)
    # Di sini kita simulasikan dengan insert manual ke tabel relasi
    print("\n--- Menambahkan Relasi M2M ---")
    try:
        # Budi mengambil Matematika dan Fisika
        cr.execute("INSERT INTO res_student_course_rel (student_id, course_id) VALUES (%s, %s)", (student1.id, course_math.id))
        cr.execute("INSERT INTO res_student_course_rel (student_id, course_id) VALUES (%s, %s)", (student1.id, course_phys.id))
        # Ani hanya mengambil Matematika
        cr.execute("INSERT INTO res_student_course_rel (student_id, course_id) VALUES (%s, %s)", (student2.id, course_math.id))
        conn.commit()
        print("SUCCESS: Relasi berhasil dibuat.")
    except Exception as e:
        print(f"ERROR: Gagal membuat relasi: {e}")
        conn.rollback()

    # 3. Membaca dan menampilkan data relasi
    print("\n--- Membaca Relasi dari Sisi Mahasiswa ---")
    budi = env['res.student'].browse(student1.id)
    print(f"Mahasiswa: {budi.name}")
    for course in budi.course_ids:
        print(f" - Mengambil Mata Kuliah: {course.name}")

    ani = env['res.student'].browse(student2.id)
    print(f"\nMahasiswa: {ani.name}")
    for course in ani.course_ids:
        print(f" - Mengambil Mata Kuliah: {course.name}")

    print("\n--- Membaca Relasi dari Sisi Mata Kuliah ---")
    math = env['res.course'].browse(course_math.id)
    print(f"Mata Kuliah: {math.name}")
    for student in math.student_ids:
        print(f" - Diikuti oleh: {student.name}")

    phys = env['res.course'].browse(course_phys.id)
    print(f"\nMata Kuliah: {phys.name}")
    for student in phys.student_ids:
        print(f" - Diikuti oleh: {student.name}")

    cr.close()

if __name__ == "__main__":
    run_many2many_example()
