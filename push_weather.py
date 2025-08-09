
import os
import requests
from urllib.parse import quote
from linebot import LineBotApi
from linebot.models import TextSendMessage

LINE_TOKEN = os.getenv('LINE_TOKEN')
CWB_API_KEY = os.getenv('CWB_API_KEY')
EPA_API_KEY = os.getenv('EPA_API_KEY')
if not EPA_API_KEY:
    print("錯誤：找不到 EPA_API_KEY 環境變數。")
line_bot_api = LineBotApi(LINE_TOKEN)

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
        url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001?Authorization={CWB_API_KEY}&format=JSON&StationId=466920&WeatherElement=UVIndex&GeoInfo="
        res = requests.get(url).json()

        stations = data.get("records", {}).get("Station") or []
        if not stations:
            return "⚠️ 無法取得紫外線資料（records 欄位為空）"

        # 如果有給 station_name，試著在 stations 中找到該站；否則取第一筆
        if station_name:
            record = next((s for s in stations if s.get("StationName") == station_name), stations[0])
        else:
            record = stations[0]

        # WeatherElement 裡面應包含 UVIndex（依你提供範例）
        weather_elem = record.get("WeatherElement") or {}
        uv_raw = weather_elem.get("UVIndex")

        if uv_raw is None:
            # 若欄位不存在，嘗試取其他可能名稱（兼容性）
            uv_raw = weather_elem.get("UVI") or weather_elem.get("UV")

        if uv_raw is None:
            return "⚠️ 紫外線資料缺失"

        # 解析成數字做分級判斷
        try:
            uv_val = float(uv_raw)
        except Exception:
            # 若無法轉數字，仍回傳原始字串但標示等級為未知
            return f"☀️ 紫外線指數：{uv_raw}（等級未知）"

        # 分級（依照你給的圖示）
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

        # 回傳格式：數值 + (等級)
        # 若數值為整數就顯示整數，不然顯示一位小數
        uv_display = int(uv_val) if uv_val.is_integer() else round(uv_val, 1)
        return f"☀️ 紫外線指數：{uv_display}（{level}）"
    except Exception as e:
        return f"⚠️ 紫外線資料取得失敗：{e}"


def get_air_quality():
    url = (
        f"https://data.moenv.gov.tw/api/v2/aqx_p_432"
        f"?format=JSON&offset=0&api_key={EPA_API_KEY}"
    )

    try:
        res = requests.get(url)
        res.raise_for_status()  # 如果請求失敗會拋出例外
        data = res.json()

        if 'records' not in data or not data['records']:
            return "⚠️ 無法取得空氣品質資料"

        # 使用列表推導式篩選出 "中山" 測站的資料
        zhongshan_records = [
            record for record in data["records"] if record["sitename"] == "中山"
        ]

        if not zhongshan_records:
            return "⚠️ 找不到中山測站的空氣品質資料"

        # 從篩選後的列表中取出第一筆資料
        site = zhongshan_records[0]
        sitename = site.get('sitename', 'N/A')
        aqi = site.get('aqi', 'N/A')
        status = site.get('status', '未知')
        
        return f"🌫️ {sitename}測站空氣品質指數（AQI）：{aqi}（{status}）"

    except requests.exceptions.RequestException as e:
        return f"⚠️ 網路連線錯誤：{e}"
    except Exception as e:
        return f"⚠️ 發生未知錯誤：{e}"
    
def main():
    weather = get_weather()
    uv = get_uv_index()
    air = get_air_quality()
    message = f"{weather}\n{uv}\n{air}"

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
