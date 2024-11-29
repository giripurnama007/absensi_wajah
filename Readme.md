# Aplikasi Absensi Wajah

Aplikasi **Absensi Wajah** adalah sistem berbasis Python untuk mendeteksi, mengenali wajah, dan mencatat kehadiran pengguna menggunakan kamera dan database MySQL. Aplikasi ini menggunakan pustaka Python seperti OpenCV dan Face Recognition untuk pengolahan gambar serta Tkinter untuk antarmuka pengguna.

---

## **Fitur**
1. **Rekam Wajah**: Menyimpan data wajah pengguna beserta informasi nama dan NIK.
2. **Absensi**: Mengenali wajah pengguna dan mencatat kehadiran ke dalam database.
3. **Laporan Kehadiran**: Menampilkan laporan kehadiran lengkap dengan nama, NIK, tanggal, dan waktu.

---

## **Persyaratan Sistem**
- **Python**: Versi 3.6 atau lebih baru
- **MySQL Server**: Untuk menyimpan data pengguna dan kehadiran
- **Kamera**: Internal atau eksternal untuk menangkap wajah pengguna

---

## **Instalasi**

### 1. **Kloning Repository**
Kloning repository ini ke komputer Anda:

git clone https://github.com/giripurnama007/absensi-wajah.git
cd absensi-wajah

### 2. **Instalasi Library Python***
Install library berikut yang dibutuhkan:
pip install opencv-python opencv-contrib-python face-recognition mysql-connector-python pillow cmake dlib