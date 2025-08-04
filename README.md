# ChatLampBot 智慧燈多模語音互動機器人

## 專案簡介

ChatLampBot 是一個結合 Azure OpenAI、語音合成、翻譯、天氣查詢與 LINE Bot 的互動平台。支援多模型聊天、情緒分析、語音播放、天氣查詢等功能。

## 主要功能

- 支援多種 AI 聊天模型（Azure、Gemini、Ollama 等），可根據需求切換。
- 整合 Azure 語音合成服務，將文字即時轉換為語音並播放。
- 提供文字翻譯及音譯功能，支援多語言互譯（如中、英、日）。
- 連結中央氣象局 OpenData，查詢各地即時天氣資訊。
- 可與 LINE Bot 互動，實現跨平台訊息溝通。
- 燈光因應聊天情境互動、情緒分析顯示、語音播放等互動式 UI。
- 內建 Flask CLI 指令，方便開發者快速查詢天氣或執行維運操作。

## 資料流

#### 1. 使用者互動（前端）

- 使用者在網頁前端輸入訊息、選擇聊天模型或查詢天氣。
- 前端將資料透過 AJAX 送到 Flask 後端 API。

---

#### 2. 後端處理（Flask）

- 後端根據使用者選擇的聊天模型，進行：
  - 多模型聊天（Azure、Gemini、Ollama）
  - 情緒分析（Azure Text Analytics）
  - 語音合成（Azure Speech）
  - 文字翻譯（Azure Translator）
  - 天氣查詢（CWA OpenData）

---

#### 3. 資料回傳（API Response）

- 後端將處理結果（如聊天回覆、情緒分數、語音檔案路徑、翻譯結果、天氣資料等）以 JSON 格式回傳給前端。

---

#### 4. 前端顯示

- 前端根據回傳資料，更新 UI：
  - 顯示聊天回覆、情緒分析、語音播放按鈕、翻譯結果、天氣資訊。
  - 觸發燈箱 modal、語音播放、燈泡狀態改變等互動效果。

---

#### 5. CLI 指令（開發/維運）

- 開發者可用 Flask CLI 指令（如 `flask weather --sites 基隆 台北`）直接查詢天氣，結果顯示於終端機。

---

## 安裝與啟動

1. 安裝 Python 套件：

   ```bash
   pip install -r requirements.txt
   ```

2. 設定環境變數或 .flaskenv：

   ```
   FLASK_APP=app.py
   FLASK_ENV=development
   ```

3. 啟動 Flask 伺服器：

   ```bash
   flask run
   ```

4. 前端請瀏覽：http://127.0.0.1:5008

## CLI 指令

可用 Flask CLI 執行天氣查詢：

```bash
flask weather --sites 基隆 台北
flask weather --all_sites
```
