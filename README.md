# Belajar Python untuk Odoo

Repository ini adalah catatan perjalanan dan ruang kerja untuk mempelajari fundamental Python yang paling relevan untuk pengembangan Odoo.

## Struktur Proyek

- `Dockerfile`: Mendefinisikan lingkungan belajar kita yang terisolasi menggunakan Docker. Ini memastikan kita memiliki environment yang konsisten dengan Python dan tools yang dibutuhkan.
- `*.py`: File-file latihan Python, diurutkan berdasarkan nomor untuk diikuti secara bertahap.
- `README.md`: File ini, berisi panduan dan catatan.

## Panduan Setup & Menjalankan Latihan

Proses ini dibagi menjadi dua bagian: setup awal (hanya dilakukan sekali) dan siklus belajar harian.

### Bagian 1: Setup Awal (Sekali Jalan)

1.  **Konfigurasi Git (Lakukan di Mesin Host Anda)**:
    Sebelum melakukan push pertama, konfigurasikan nama dan email Anda. Jalankan perintah ini di terminal Anda:
    ```bash
    git config --global user.name "n0tx"
    git config --global user.email "rcandra91@msn.com"
    ```

2.  **Push Commit Pertama ke GitHub**:
    Setelah file-file awal dibuat, simpan pekerjaan Anda ke GitHub.
    ```bash
    git push -u origin main
    ```

3.  **Build Image Docker**:
    Dari direktori root proyek (`learn-odoo-python`), bangun image Docker yang akan menjadi sandbox kita.
    ```bash
    docker build -t odoo-learn-env .
    ```

4.  **Jalankan Container Docker**:
    Jalankan container dari image yang baru saja dibuat. Container ini akan berjalan di background.
    ```bash
    # Perintah ini memasang direktori saat ini ke /usr/src/app di dalam container
    docker run -d --name odoo-sandbox -v "$(pwd):/usr/src/app" odoo-learn-env
    ```

### Bagian 2: Siklus Belajar (Ulangi Sesuai Kebutuhan)

1.  **Masuk ke Dalam Sandbox (Container)**:
    Untuk memulai sesi belajar, masuk ke dalam shell container yang sedang berjalan.
    ```bash
    docker exec -it odoo-sandbox /bin/bash
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

4.  **Mematikan Container**:
    Jika Anda ingin mematikan sandbox untuk menghemat resource, jalankan dari mesin host:
    ```bash
    docker stop odoo-sandbox
    ```
    Untuk menyalakannya lagi nanti:
    ```bash
    docker start odoo-sandbox
    ```
---
*Dokumen ini dibuat dan diperbarui secara kolaboratif dengan Gemini.*
