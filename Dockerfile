# 使用 Python 3.12 作為基礎映像
FROM python:3.12-slim

# 設定工作目錄
WORKDIR /app

# 複製 requirements.txt 並安裝 Python 依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製專案檔案
COPY . .

# 建立必要的目錄
RUN mkdir -p static/speech

# 設定環境變數
ENV PYTHONPATH=/app

# 暴露端口
EXPOSE 5003

# 健康檢查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=1 \
    CMD curl -f http://127.0.0.1:5003/ || exit 1

# 預設啟動主應用（可由 docker-compose 覆蓋）
CMD ["gunicorn", "-k", "eventlet", "-w", "1", "-b", "0.0.0.0:5003", "app:app"]