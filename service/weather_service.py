import requests 
from datetime import datetime

class WeatherService:
    """
    天氣查詢服務，整合中央氣象局開放資料 API。
    """
    A0001_URL = None
    A0003_URL = None
    AUTHORIZATION = None

    def __init__(self, config):
        self.config = config
        self.A0001_URL = self.config["Weather"]["A0001_URL"]
        self.A0003_URL = self.config["Weather"]["A0003_URL"]
        self.AUTHORIZATION = self.config["Weather"]["AUTHORIZATION"]
        
        self.data = {'A0001_URL': None, 'A0003_URL': None}
        self.stations_data = {'A0001_URL': [], 'A0003_URL': []}
        

    def get_data(self):
        """取得原始氣象資料。"""
        return self.data

    def get_stations_data(self):
        """取得所有測站名稱。"""
        return self.stations_data

    def _get_opendata_cwa(self, target):
        """從中央氣象局 API 取得資料。"""
        parameters = {'Authorization': self.AUTHORIZATION}
        request = requests.get(getattr(self, target), params=parameters, verify=False)
        content_type = request.headers['Content-Type']
        if request.status_code != 200:
            raise Exception(f"Error fetching data: {request.status_code} - {request.text}")
        elif not content_type.startswith('application/json'):
            raise Exception("Response is not in JSON format " + str(content_type))
        else:
            data = request.json()
            self.data[target] = data
            stations = data['records']['Station']
            self.stations_data[target] = [station['StationName'] for station in stations]
            return data

    def get_station_weather(self, stationName='臺北'):
        """查詢指定測站的即時天氣資訊。"""
        result = {'S': None, 'T': None, 'H': None, 'R': None, 'O': None}
        station_data = self.find_station_data(self.data, stationName)
        if station_data is None:
            return result
        obs_time_iso = station_data['ObsTime']['DateTime']
        obs_time_datetime = datetime.fromisoformat(obs_time_iso)
        obs_time_datetime = obs_time_datetime.strftime("%m/%d %H:%M")
        air_temperature = float(station_data['WeatherElement']['AirTemperature'])
        relative_humidity = float(station_data['WeatherElement']['RelativeHumidity']) / 100
        precipitation = float(station_data['WeatherElement']['Now']['Precipitation'])
        result['S'] = stationName
        result['T'] = air_temperature
        result['H'] = relative_humidity
        result['R'] = precipitation
        result['O'] = obs_time_datetime
        return result

    def set_default_opendata_cwa(self):
        self._get_opendata_cwa('A0001_URL')
        self._get_opendata_cwa('A0003_URL')
        
        return self
        
      
    def find_station_data(self, data, stationName):
        """依測站名稱查找資料。"""
        if data['A0001_URL'] is None:
            self._get_opendata_cwa('A0001_URL')
        station_data = self._find_station_data(data['A0001_URL'], stationName)
        if station_data is None:
            if data['A0003_URL'] is None:
                self._get_opendata_cwa('A0003_URL')
            station_data = self._find_station_data(data['A0003_URL'], stationName)
        return station_data

    def _find_station_data(self, data, stationName):
        """回傳指定測站的原始資料(dict)。"""
        stations = data['records']['Station']
        for station in stations:
            if station['StationName'] == stationName:
                return station
        return None
    
    def render_station_data(self, station_data):
        """將測站資料轉換為可讀格式。"""
        if station_data is None or station_data['S'] is None:
            return "測站資料不存在"
        
        station_data['H'] = '' if station_data['H'] is None else station_data['H'] * 100
        
        return f"測站: {station_data['S']}, 溫度: {station_data['T']}°C, 濕度: {(station_data['H'])}%, 降雨量: {station_data['R']}mm, 時間: {station_data['O']}"


if __name__ == "__main__":
    pass