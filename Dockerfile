# 使用 Python 3.12 作為基礎映像
FROM python:3.12

# 安裝 envsubst
RUN apt-get update && apt-get install -y gettext

# 設定工作目錄
WORKDIR /app

# 複製 requirements.txt 並安裝 Python 依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir supervisor

# 複製專案檔案
COPY . .

# 複製 supervisord.conf 設定檔
COPY supervisord.conf.template /app/supervisord.conf.template
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# 建立必要的目錄
RUN mkdir -p static/speech

# 設定環境變數
ENV PYTHONPATH=/app

# 暴露端口
EXPOSE ${PORT_CHATLAMPBOT}

# 健康檢查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=1 \
    CMD curl -f http://127.0.0.1:${PORT_CHATLAMPBOT}/ || exit 1

# 預設啟動主應用（可由 docker-compose 覆蓋）
ENTRYPOINT ["/app/docker-entrypoint.sh"]