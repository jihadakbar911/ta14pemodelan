# 🚗 Simulasi Drive-Thru Restaurant - Streamlit App

Aplikasi web interaktif untuk simulasi dan analisis sistem antrian drive-thru menggunakan SimPy dan Streamlit.

## 📋 Deskripsi

Aplikasi ini mensimulasikan sistem antrian drive-thru restoran cepat saji dengan parameter yang dapat disesuaikan. User dapat:
- Mengatur parameter kedatangan (distribusi eksponensial)
- Mengatur waktu layanan (distribusi uniform)
- Membandingkan berbagai skenario (jumlah loket berbeda)
- Melihat visualisasi hasil (histogram, box plot, line chart)
- Mendapatkan analisis cost-benefit dan rekomendasi
- Download hasil simulasi dalam format CSV

## 🚀 Cara Deploy ke Streamlit Cloud

### Prasyarat
1. **Akun GitHub** (gratis)
2. **Akun Streamlit Cloud** (gratis) - daftar di [share.streamlit.io](https://share.streamlit.io)

### Langkah-langkah Deployment:

#### 1. Upload ke GitHub
```bash
# Inisialisasi git repository (jika belum)
cd "c:\Tugas Kuliah\SEMESTER 5\Praktikum Pemodelan dan Simulasi\Pertemuan 14\TA-14"
git init

# Tambahkan file
git add app.py requirements.txt README.md

# Commit
git commit -m "Initial commit: Drive-Thru Simulation App"

# Buat repository baru di GitHub dan push
git remote add origin https://github.com/USERNAME/REPO-NAME.git
git branch -M main
git push -u origin main
```

#### 2. Deploy di Streamlit Cloud
1. Buka [share.streamlit.io](https://share.streamlit.io)
2. Login dengan akun GitHub
3. Klik **"New app"**
4. Pilih:
   - **Repository:** USERNAME/REPO-NAME
   - **Branch:** main
   - **Main file path:** app.py
5. Klik **"Deploy!"**
6. Tunggu beberapa menit hingga deployment selesai
7. Aplikasi akan tersedia di URL: `https://USERNAME-REPO-NAME.streamlit.app`

## 💻 Menjalankan Secara Lokal

### Instalasi Dependencies
```bash
pip install -r requirements.txt
```

### Menjalankan Aplikasi
```bash
streamlit run app.py
```

Aplikasi akan terbuka di browser pada `http://localhost:8501`

## 📊 Fitur Aplikasi

### 1. Konfigurasi Parameter (Sidebar)
- **Kedatangan:** Rata-rata waktu antar kedatangan (distribusi eksponensial)
- **Layanan:** Range waktu layanan min-max (distribusi uniform)
- **Simulasi:** Total waktu dan warm-up period
- **Skenario:** Jumlah loket untuk skenario A dan B
- **Random Seed:** Untuk reproducibility

### 2. Tab "Info & Parameter"
- Identifikasi studi kasus
- Formulir desain simulasi
- Parameter yang digunakan

### 3. Tab "Hasil Simulasi"
- Metrics cards (total mobil, rata-rata tunggu, utilization)
- Statistik deskriptif lengkap
- Tabel perbandingan skenario dengan improvement percentage

### 4. Tab "Visualisasi"
- **Histogram:** Distribusi waktu tunggu
- **Box Plot:** Perbandingan waktu tunggu dan total waktu
- **Line Chart:** Panjang antrian seiring waktu

### 5. Tab "Kesimpulan"
- Temuan utama dengan metrics improvement
- Analisis cost-benefit
- Rekomendasi berdasarkan hasil
- Download data CSV

## 🛠️ Teknologi yang Digunakan

- **SimPy:** Framework discrete-event simulation
- **Streamlit:** Web framework untuk data apps
- **NumPy:** Random number generation
- **Pandas:** Data manipulation
- **Matplotlib & Seaborn:** Visualisasi data

## 📁 Struktur File

```
TA-14/
├── app.py                           # Aplikasi Streamlit utama
├── requirements.txt                 # Python dependencies
├── README.md                        # Dokumentasi
└── TP14_Simulasi_DriveThru.ipynb   # Jupyter notebook (untuk analisis offline)
```

## 🎓 Info Tugas

**Mata Kuliah:** Praktikum Pemodelan dan Simulasi  
**Tugas:** TP-14 (Formulir Desain Simulasi SimPy)  
**Topik:** Analisis Antrian Drive-Thru Restaurant

## 📝 Catatan

- Untuk hasil terbaik, gunakan warm-up period minimal 100 menit
- Total waktu simulasi yang lebih lama (>1000 menit) memberikan hasil lebih stabil
- Gunakan random seed yang sama untuk fair comparison antar skenario
- Aplikasi akan menyimpan hasil simulasi terakhir di session state

## 🐛 Troubleshooting

**Masalah:** Aplikasi loading lama
- **Solusi:** Kurangi total waktu simulasi atau warm-up period

**Masalah:** Error saat deploy di Streamlit Cloud
- **Solusi:** Pastikan requirements.txt ada dan lengkap

**Masalah:** Grafik tidak muncul
- **Solusi:** Pastikan sudah klik tombol "Jalankan Simulasi"

## 📧 Support

Jika ada pertanyaan atau masalah, silakan buat issue di GitHub repository.

---

**© 2026 | Praktikum Pemodelan dan Simulasi**
