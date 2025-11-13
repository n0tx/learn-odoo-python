# Belajar Python untuk Odoo

Repository ini adalah catatan perjalanan dan ruang kerja untuk mempelajari fundamental Python yang paling relevan untuk pengembangan Odoo.

## Struktur Proyek

- `Dockerfile`: Mendefinisikan lingkungan Python kita.
- `docker-compose.yml`: Mengatur dan menghubungkan layanan aplikasi Python dan database PostgreSQL.
- `*.py`: File-file latihan Python, diurutkan berdasarkan nomor untuk diikuti secara bertahap.
- `README.md`: File ini, berisi panduan dan catatan.

## Panduan Setup & Menjalankan Latihan

Dengan Docker Compose, prosesnya menjadi lebih sederhana.

### Bagian 1: Setup Awal (Sekali Jalan)

1.  **Konfigurasi Git (Lakukan di Mesin Host Anda)**:
    Jika belum, konfigurasikan nama dan email Anda:
    ```bash
    git config --global user.name "n0tx"
    git config --global user.email "rcandra91@msn.com"
    ```

2.  **Jalankan Lingkungan Docker Compose**:
    Dari direktori root proyek, perintah ini akan membangun image (jika belum ada) dan menjalankan semua layanan (aplikasi Python & database) di background.
    ```bash
    docker-compose up -d
    ```

### Bagian 2: Siklus Belajar (Ulangi Sesuai Kebutuhan)

1.  **Masuk ke Dalam Sandbox (Container Aplikasi)**:
    Untuk memulai sesi belajar, masuk ke dalam shell container `odoo` yang sedang berjalan.
    ```bash
    docker-compose exec odoo /bin/bash
    ```
    Prompt terminal Anda akan berubah, menandakan Anda sekarang berada di dalam container.

2.  **Jalankan File Latihan Python**:
    Di dalam container, Anda bisa melihat semua file proyek. Jalankan file latihan yang relevan.
    ```bash
    # Cek isi direktori
    ls -l

    # Jalankan file latihan pertama
    python 01_data_types_and_structures.py
    ```

3.  **Keluar dari Sandbox**:
    Jika sudah selesai, ketik `exit` dan tekan Enter untuk kembali ke terminal mesin host Anda.
    ```bash
    exit
    ```

4.  **Mematikan Lingkungan**:
    Jika Anda ingin mematikan seluruh layanan (aplikasi dan database) untuk menghemat resource, jalankan dari mesin host:
    ```bash
    docker-compose down
    ```
    Untuk menyalakannya lagi nanti, cukup jalankan kembali `docker-compose up -d`.
---
*Dokumen ini dibuat dan diperbarui secara kolaboratif dengan Gemini.*
