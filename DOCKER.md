# ChatLampBot 智慧燈多模語音互動機器人 - Docker 部署說明

## 使用 Docker 快速部署

### 方法一：使用 Docker Compose（推薦）

```bash
# 1. 確保 config.ini 設定正確
cp config.ini.example config.ini
# 編輯 config.ini，填入您的 API 金鑰

# 2. 啟動服務
docker-compose up -d

# 3. 查看日誌
docker-compose logs -f

# 4. 停止服務
docker-compose down
```

### 方法二：直接使用 Docker

```bash
# 1. 建構映像檔
docker build -t chatlampbot .

# 2. 啟動容器
docker run -d \
  --name chatlampbot \
  -p 5008:5008 \
  -v $(pwd)/config.ini:/app/config.ini:ro \
  -v $(pwd)/static/speech:/app/static/speech \
  chatlampbot

# 3. 查看日誌
docker logs -f chatlampbot

# 4. 停止容器
docker stop chatlampbot
docker rm chatlampbot
```

### 服務端點

- **主要服務**: http://127.0.0.1:5008
- **Webhook 服務** (如啟用): http://127.0.0.1:5004

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
   docker exec -it chatlampbot curl -f http://127.0.0.1:5008/
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
        proxy_pass http://127.0.0.1:5008;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```
