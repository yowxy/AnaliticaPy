# Gunakan Python 3.11 versi slim (ringan)
FROM python:3.11-slim

# Set direktori kerja di dalam container
WORKDIR /app

# Copy requirements dulu (supaya layer cache lebih efisien)
COPY requirements.txt .

# Install semua library Python
RUN pip install --no-cache-dir -r requirements.txt

# Copy semua file project ke dalam container
COPY . .

# Buka port 5000 (port Flask)
EXPOSE 5000

# Jalankan aplikasi saat container start
CMD ["python", "app.py"]
