import configparser

class URLHelper:
    """URL 管理工具類，統一處理 HTTP/HTTPS 切換"""
    
    def __init__(self, config: configparser.ConfigParser):
        self.config = config
    
    def _get_protocol(self, section: str) -> str:
        """根據 SSL_ENABLED 設定決定使用 http 或 https"""
        ssl_enabled = self.config.getboolean(section, "SSL_ENABLED", fallback=False)
        return "https" if ssl_enabled else "http"
    
    def get_base_urls(self) -> dict:
        """取得 Base 區段的所有 URL"""
        protocol = self._get_protocol("Base")
        domain = self.config.get("Base", "DOMAIN", fallback="127.0.0.1")
        base_path = self.config.get("Base", "BASE_PATH", fallback="")
        base_path = '/' + base_path if base_path else ''
        
        main_port = self.config.get("Base", "PORT_CHATLAMPBOT", fallback="5003")
        webhook_port = self.config.get("Base", "PORT_CHATLAMPBOT_WEBHOOK", fallback="5004")
        main_port = ':' + main_port if main_port and main_port != '80' else ''
        webhook_port = ':' + webhook_port if webhook_port and main_port != '' else ''

        main_url = f"{protocol}://{domain}{main_port}{base_path}"
        webhook_url = f"{protocol}://{domain}{webhook_port}"
        
        return {
            "WEBHOOK_URL": f"{webhook_url}",  # Socket.IO 連接用
            "WEBHOOK_PATH_URL": f"{base_path}/webhook",  # Socket.IO 連接用
            "WEB_URL": main_url,         # 主頁面 URL
            "API_URL": f"{main_url}/api", # API 端點
            "AUDIO_URL": f"{main_url}/static/speech", # 音頻檔案
            "STATIC_URL": f"{main_url}/static",        # 靜態檔案
            "DOMAIN": domain
        }

    
    def get_deploy_url(self) -> str:
        """取得 Deploy 區段的 URL"""
        protocol = self._get_protocol("Deploy")
        domain = self.config.get("Deploy", "DOMAIN", fallback=self.config.get("Base", "DOMAIN", fallback="127.0.0.1"))
        base_path = self.config.get("Deploy", "BASE_PATH", fallback=self.config.get("Base", "BASE_PATH", fallback=""))
        main_port = self.config.get("Deploy", "PORT", fallback=self.config.get("Base", "PORT_CHATLAMPBOT", fallback="5003"))
        main_port = ':' + main_port if main_port else ''
        
        return f"{protocol}://{domain}{main_port}{base_path}"
    
    def get_ollama_client_url(self) -> str:
        """取得 Ollama 客戶端 URL"""
        protocol = self._get_protocol("OllamaLLM")
        host = self.config.get("OllamaLLM", "OLLAMA_HOST", fallback="ollama:11434")
        
        if host.startswith(("http://", "https://")):
            return host
        
        return f"{protocol}://{host}"


def get_url_helper(config: configparser.ConfigParser) -> URLHelper:
    """工廠方法，建立 URLHelper 實例"""
    return URLHelper(config)
