# ChatLampBot 智慧燈多模語音互動機器人 - Docker 部署說明

## 使用 Docker Compose 快速部署（推薦）

```bash
# 1. 建構並啟動所有服務
docker-compose up -d

# 2. 查看服務狀態
docker-compose ps

# 3. 查看日誌
docker-compose logs -f

# 4. 停止所有服務
docker-compose down
```

## 使用 Docker 單獨部署

```bash
# 1. 建構映像檔
docker build -t chatlampbot .

# 2. 啟動主要服務（LINE Bot）
docker run -d \
  --name chatlampbot-main \
  -p 5003:5003 \
  -v $(pwd)/config.ini:/app/config.ini:ro \
  -v $(pwd)/static/speech:/app/static/speech \
  chatlampbot

# 3. 啟動 Webhook 服務
docker run -d \
  --name chatlampbot-webhook \
  -p 5004:5004 \
  -v $(pwd)/config.ini:/app/config.ini:ro \
  -v $(pwd)/static/speech:/app/static/speech \
  chatlampbot \
  gunicorn -k eventlet -w 1 -b 0.0.0.0:5004 app_webhook:app

# 4. 查看日誌
docker logs -f chatlampbot-main
docker logs -f chatlampbot-webhook

# 5. 停止容器
docker stop chatlampbot-main chatlampbot-webhook
docker rm chatlampbot-main chatlampbot-webhook
```

### 服務端點

- **主要服務（LINE Bot）**: <http://127.0.0.1:5003>
- **Webhook 服務（SocketIO）**: <http://127.0.0.1:5004>

### CLI 命令使用

即使在容器中，您也可以使用 Flask CLI 命令：

```bash
# 天氣查詢
docker exec -it chatlampbot flask weather --site 台北
docker exec -it chatlampbot flask weather --site 新北
docker exec -it chatlampbot flask weather --site 台中

# 查看所有命令
docker exec -it chatlampbot flask --help
```

### 檔案掛載說明

- `config.ini`: 只讀掛載，確保設定安全性
- `static/speech`: 讀寫掛載，用於儲存生成的語音檔案

### 故障排除

1. **容器無法啟動**

   ```bash
   docker logs chatlampbot
   ```

2. **設定檔案錯誤**

   ```bash
   # 檢查設定檔
   docker exec -it chatlampbot cat /app/config.ini
   ```

3. **網路連接問題**
   ```bash
   # 測試容器網路
   docker exec -it chatlampbot curl -f http://127.0.0.1:5003/
   ```

### 生產環境建議

1. 使用 nginx 作為反向代理
2. 設定 SSL 憑證
3. 配置日誌輪替
4. 定期備份設定檔案

```nginx
# nginx 設定範例
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5003;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```
