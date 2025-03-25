# 使用官方 Python 3.10 基礎映像
FROM python:3.10

# 設定工作目錄
WORKDIR /app

# 複製專案文件
COPY . /app

# 安裝系統套件
RUN apt-get update && apt-get install -y libpq-dev && rm -rf /var/lib/apt/lists/*

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 設定環境變數，避免 Python 產生緩存
ENV PYTHONUNBUFFERED=1

# 啟動 Django 應用
#CMD ["gunicorn", "--bind", "0.0.0.0:8000", "short_url_service.wsgi:application"]

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "shortUrl.wsgi:application"]