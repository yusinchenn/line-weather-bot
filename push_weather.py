import os
import requests
from urllib.parse import quote
from linebot import LineBotApi
from linebot.models import TextSendMessage

LINE_TOKEN = os.getenv('LINE_TOKEN')
CWB_API_KEY = os.getenv('CWB_API_KEY')
EPA_API_KEY = os.getenv('EPA_API_KEY')

from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    BroadcastRequest,
    TextMessage
)

def get_weather():
    try:
        url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={CWB_API_KEY}&locationName=臺北市"
        res = requests.get(url).json()
        elements = res['records']['location'][0]['weatherElement']
        wx = elements[0]['time'][0]['parameter']['parameterName']
        min_temp = elements[2]['time'][0]['parameter']['parameterName']
        max_temp = elements[4]['time'][0]['parameter']['parameterName']
        rain_prob = elements[1]['time'][0]['parameter']['parameterName']
        
        return f"🌤️ 今日天氣：{wx}\n🌡️ 溫度：{min_temp}°C - {max_temp}°C\n☔ 降雨機率：{rain_prob}%"
        
    except Exception as e:
        return f"⚠️ 天氣資料取得失敗：{e}"

def get_uv_index():
    try:
        url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001?Authorization={CWB_API_KEY}&format=JSON&StationId=466920"
        data = requests.get(url).json()
        uv_val = int(data["records"]["Station"][0]["WeatherElement"]["UVIndex"])

        # UV 等級判斷
        if uv_val <= 2:
            level = "低量級"
        elif uv_val <= 5:
            level = "中量級"
        elif uv_val <= 7:
            level = "高量級"
        elif uv_val <= 10:
            level = "過量級"
        else:
            level = "危險級"
            
        return f"🌞 紫外線指數：{uv_val}（{level}）"
        
    except Exception as e:
        return f"⚠️ 紫外線資料取得失敗：{e}"

def get_air_quality():
    try:
        # 建議使用 aqx_p_432 (全台空氣品質指標)，因為它直接包含計算好的 AQI 與狀態
        # 如果您堅持要用 aqx_p_200，請將下方的 432 改為 200，但欄位可能需要調整
        url = "https://data.moenv.gov.tw/api/v2/aqx_p_432"
        
        params = {
            "format": "json",
            "offset": "0",
            "limit": "1000",
            "api_key": EPA_API_KEY
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # --- 核心修正：自動判斷回傳格式 ---
        records = []
        if isinstance(data, list):
            # 情況 A: API 直接回傳列表 (如您錯誤訊息所示)
            records = data
        elif isinstance(data, dict):
            # 情況 B: API 回傳字典，資料在 records 欄位中
            records = data.get("records", [])
        else:
            return f"⚠️ API 回傳格式無法解析: {type(data)}"
        # -------------------------------

        # 尋找「中山」測站 (同時支援 sitename 與 SiteName)
        target_station = next(
            (r for r in records if r.get("sitename") == "中山" or r.get("SiteName") == "中山"), 
            None
        )

        if not target_station:
            return "⚠️ 找不到「中山」測站的空氣品質資料"

        # 取得 AQI 與 狀態 (同時支援大小寫 key)
        aqi = target_station.get('aqi') or target_station.get('AQI') or 'N/A'
        status = target_station.get('status') or target_station.get('Status') or '未知'
        
        return f"🌫️ 空氣品質指數（AQI）：{aqi}（{status}）"

    except Exception as e:
        return f"⚠️ 空氣品質資料取得失敗：{e}"
    
def main():
    weather = get_weather()
    uv = get_uv_index()
    air = get_air_quality()
    message = f"{weather}\n{uv}\n{air}"
    print(message)

    configuration = Configuration(access_token=LINE_TOKEN)
    with ApiClient(configuration) as api_client:
        messaging_api = MessagingApi(api_client)
        broadcast_request = BroadcastRequest(
            messages=[TextMessage(text=message)]
        )
        try:
            messaging_api.broadcast(broadcast_request)
            print("LINE 訊息廣播成功！")
        except Exception as e:
            print(f"LINE 訊息廣播失敗：{e}")


if __name__ == "__main__":
    main()
