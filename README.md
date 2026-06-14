# AnaliticaPy

Dashboard analitik data penjualan e-commerce berbasis web, dibangun dengan Python dan Flask. Menampilkan visualisasi interaktif dari data transaksi secara real-time melalui antarmuka browser.

---

## Apa yang dilakukan aplikasi ini

AnaliticaPy menghasilkan data penjualan sintetis (500 transaksi) yang mencakup 5 kategori produk dan 5 kota di Indonesia, lalu menyajikannya dalam bentuk grafik dan tabel melalui REST API yang dikonsumsi oleh frontend HTML.

**Visualisasi yang tersedia:**

| Chart | Keterangan |
|---|---|
| Tren Pendapatan | Pendapatan bulanan sepanjang tahun |
| Pendapatan per Kategori | Perbandingan antar kategori produk |
| Performa per Kota | Unit terjual vs pendapatan per kota |
| Rating Produk | Rata-rata rating per kategori |
| Heatmap Penjualan | Distribusi unit terjual per kategori per bulan |

**Ringkasan statistik yang ditampilkan:** total pendapatan, total transaksi, total unit terjual, rata-rata rating, kategori terlaris, dan kota dengan pendapatan tertinggi.

---

## Teknologi yang digunakan

- **Python 3.11** — bahasa utama
- **Flask 3.0** — web framework & REST API
- **Pandas 2.1** — manipulasi dan agregasi data
- **Matplotlib 3.8** — render chart ke gambar PNG (base64)
- **NumPy 1.26** — generasi data acak
- **Docker** — containerisasi aplikasi

---

## Struktur Proyek

```
AnaliticaPy/
├── app.py               # Logika utama: data, chart, dan API endpoint
├── index.html           # Frontend dashboard
├── requirements.txt     # Dependensi Python
├── Dockerfile           # Image Docker
├── docker-compose.yml   # Konfigurasi container
└── .env                 # Variabel lingkungan
```

---

## Cara Menjalankan

### Menggunakan Docker (direkomendasikan)

Pastikan Docker dan Docker Compose sudah terinstal.

```bash
git clone https://github.com/yowxy/AnaliticaPy.git
cd AnaliticaPy
docker-compose up --build
```

Akses aplikasi di: `http://localhost:5000`

### Tanpa Docker

```bash
git clone https://github.com/yowxy/AnaliticaPy.git
cd AnaliticaPy
pip install -r requirements.txt
python app.py
```

Akses aplikasi di: `http://localhost:5000`

---

## API Endpoint

| Method | Endpoint | Respons |
|---|---|---|
| GET | `/` | Halaman dashboard utama |
| GET | `/api/summary` | Statistik ringkasan (JSON) |
| GET | `/api/charts/tren` | Chart tren pendapatan (base64 PNG) |
| GET | `/api/charts/kategori` | Chart per kategori (base64 PNG) |
| GET | `/api/charts/kota` | Chart per kota (base64 PNG) |
| GET | `/api/charts/rating` | Chart rating (base64 PNG) |
| GET | `/api/charts/heatmap` | Heatmap penjualan (base64 PNG) |
| GET | `/api/tabel` | Tabel 20 kombinasi kategori-kota terbaik (JSON) |

---

## Dependensi

```
flask==3.0.0
pandas==2.1.4
matplotlib==3.8.2
seaborn==0.13.0
numpy==1.26.2
```

---

## Catatan

Data yang digunakan adalah data sintetis yang dibangkitkan secara acak setiap kali aplikasi dijalankan. Tidak ada koneksi ke database eksternal atau sumber data nyata.

---

*Final Project — Praktikum Manajemen Data*
