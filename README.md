# Belajar Python untuk Odoo

Repository ini adalah catatan perjalanan dan ruang kerja untuk mempelajari fundamental Python yang paling relevan untuk pengembangan Odoo.

## Struktur Proyek

- `Dockerfile`: Mendefinisikan lingkungan Python kita.
- `docker-compose.yml`: (Tidak digunakan saat ini karena masalah kompatibilitas) Mengatur layanan.
- `*.py`: File-file latihan Python, diurutkan berdasarkan nomor untuk diikuti secara bertahap.
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
    sudo docker run -d --name odoo-db --network odoo-learn-net -v odoo-db-data:/var/lib/postgresql/data -e POSTGRES_PASSWORD=odoo -e POSTGRES_USER=odoo -e POSTGRES_DB=postgres postgres:13
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

2.  **Jalankan File Latihan Python**:
    Di dalam container, jalankan file latihan yang relevan.
    ```bash
    # Cek isi direktori
    ls -l

    # Jalankan file latihan pertama
    python 01_data_types_and_structures.py
    ```

3.  **Keluar dari Sandbox**:
    Jika sudah selesai, ketik `exit` dan tekan Enter.

### Bagian 3: Manajemen Lingkungan

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
