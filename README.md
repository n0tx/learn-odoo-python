# Belajar Python untuk Odoo

Repository ini adalah catatan perjalanan dan ruang kerja untuk mempelajari fundamental Python yang paling relevan untuk pengembangan Odoo.

## Struktur Proyek

- `Dockerfile`: Mendefinisikan lingkungan Python kita (sekarang termasuk library `psycopg2` untuk koneksi database).
- `docker-compose.yml`: (Tidak digunakan saat ini karena masalah kompatibilitas) Mengatur layanan.
- `*.py`: File-file latihan Python, diurutkan berdasarkan nomor untuk diikuti secara bertahap.
- `04_pengenalan_odoo_model.py`: Latihan pengenalan konsep Odoo Model (ORM) melalui simulasi.
- `05_creating_records_orm.py`: Latihan membuat data (Create) menggunakan metode ORM.
- `11_relational_fields_many2many.py`: Latihan yang menjelaskan relasi Many2many, di mana banyak record dari satu model dapat terhubung ke banyak record di model lain (contoh: mahasiswa dan mata kuliah).
- `12_business_methods.py`: Latihan yang menunjukkan cara menambahkan logika bisnis ke model melalui metode kustom (contoh: mengonfirmasi pesanan penjualan).
- `README.md`: File ini, berisi panduan dan catatan.

## Panduan Setup & Menjalankan Latihan (Metode Manual)

Karena adanya masalah kompatibilitas dengan `docker-compose`, kita akan menggunakan perintah `docker` manual. Perintah ini memerlukan `sudo`.

### Bagian 1: Setup Awal (Sekali Jalan)

1.  **Buat Jaringan Docker**:
    Buat jaringan virtual agar kontainer aplikasi dan database bisa berkomunikasi.
    ```bash
    sudo docker network create odoo-learn-net
    ```

2.  **Jalankan Kontainer Database PostgreSQL**:
    Jalankan kontainer database di latar belakang dan pastikan datanya persisten.
    ```bash
    sudo docker run -d --name odoo-db --network odoo-learn-net -v odoo-db-data:/var/lib/postgresql/data -e POSTGR_PASSWORD=odoo -e POSTGR_USER=odoo -e POSTGR_DB=postgres postgres:13
    ```

3.  **Build & Jalankan Kontainer Aplikasi Python**:
    Bangun image dari `Dockerfile` dan jalankan kontainer aplikasi.
    ```bash
    sudo docker build -t odoo-learn-env .
    sudo docker run -d --name odoo-sandbox --network odoo-learn-net -v "/home/zerobyte365/learn-odoo-python:/usr/src/app" odoo-learn-env tail -f /dev/null
    ```

### Bagian 2: Siklus Belajar (Ulangi Sesuai Kebutuhan)

1.  **Masuk ke Dalam Sandbox (Container Aplikasi)**:
    Untuk memulai sesi belajar, masuk ke dalam shell container `odoo-sandbox`.
    ```bash
    sudo docker exec -it odoo-sandbox /bin/bash
    ```
    Prompt terminal Anda akan berubah, menandakan Anda sekarang berada di dalam container.

2.  **Alur Kerja Development**:
    **PENTING**: Alur kerja yang efisien adalah sebagai berikut:
    -   **Edit Kode:** Gunakan editor teks favorit Anda (misal: VS Code, Sublime) di komputer utama (**host**) untuk mengubah file `.py`.
    -   **Jalankan Kode:** Beralih ke terminal **sandbox** (container) untuk menjalankan file Python yang sudah diubah.
    
    Berkat `volume mounting` (`-v`), setiap kali Anda menyimpan file di host, perubahannya akan langsung tersedia di dalam container.

3.  **Jalankan File Latihan Python**:
    Di dalam container, jalankan file latihan yang relevan.
    ```bash
    # Jalankan file latihan pertama
    python 01_data_types_and_structures.py

    # Jalankan file latihan kedua
    python 02_database_connection.py

    # Jalankan file latihan ketiga
    python 03_functions_and_classes.py

    # Jalankan file latihan keempat (simulasi Odoo Model)
    python 04_pengenalan_odoo_model.py

    # Jalankan file latihan kelima (membuat record)
    python 05_creating_records_orm.py

    # Jalankan file latihan keenam (membaca dan mencari record)
    python 06_reading_and_searching_records.py

    # Jalankan file latihan ketujuh (memperbarui record)
    python 07_updating_records.py

    # Jalankan file latihan kedelapan (menghapus record)
    python 08_deleting_records.py

    # Jalankan file latihan kesembilan (relasi Many2one)
    python 09_relational_fields_many2one.py

    # Jalankan file latihan kesepuluh (relasi One2many)
    python 10_relational_fields_one2many.py

    # Jalankan file latihan kesebelas (relasi Many2many)
    python 11_relational_fields_many2many.py

    # Jalankan file latihan kedua belas (business methods)
    python 12_business_methods.py
    ```

4.  **Keluar dari Sandbox**:
    Jika sudah selesai, ketik `exit` dan tekan Enter.

### Bagian 3: Manajemen Lingkungan

-   **Memperbarui Lingkungan (Jika Dockerfile Berubah)**:
    Jika Anda memodifikasi `Dockerfile` (misalnya untuk menambah library baru), Anda perlu membangun ulang image dan mengganti container lama:
    ```bash
    # 1. Bangun ulang image dengan perubahan baru
    sudo docker build -t odoo-learn-env .

    # 2. Hentikan dan hapus container lama
    sudo docker stop odoo-sandbox
    sudo docker rm odoo-sandbox

    # 3. Jalankan container baru dari image yang sudah diperbarui
    sudo docker run -d --name odoo-sandbox --network odoo-learn-net -v "/home/zerobyte365/learn-odoo-python:/usr/src/app" odoo-learn-env tail -f /dev/null
    ```

-   **Mematikan Kontainer**:
    Untuk menghentikan kedua kontainer (aplikasi dan database):
    ```bash
    sudo docker stop odoo-sandbox odoo-db
    ```

-   **Menyalakan Kontainer Kembali**:
    Untuk menyalakan kembali kontainer yang sudah ada:
    ```bash
    sudo docker start odoo-sandbox odoo-db
    ```

-   **Membersihkan (Hapus Semuanya)**:
    **PERHATIAN:** Perintah ini akan menghapus kontainer, jaringan, dan volume data database Anda secara permanen.
    ```bash
    sudo docker stop odoo-sandbox odoo-db
    sudo docker rm odoo-sandbox odoo-db
    sudo docker network rm odoo-learn-net
    sudo docker volume rm odoo-db-data
    ```
---
*Dokumen ini dibuat dan diperbarui secara kolaboratif dengan Gemini.*
