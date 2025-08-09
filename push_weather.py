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
        url = (f"https://data.moenv.gov.tw/api/v2/aqx_p_432?format=JSON&offset=0&api_key={EPA_API_KEY}")
        qua = requests.get(url).json()

        # 使用列表推導式篩選出 "中山" 測站的資料
        zhongshan_records = [
            record for record in qua["records"] if record["sitename"] == "中山"
        ]

        # 從篩選後的列表中取出第一筆資料
        site = zhongshan_records[0]
        aqi = site.get('aqi', 'N/A')
        status = site.get('status', '未知')
        
        return f"🌫️空氣品質指數（AQI）：{aqi}（{status}）"

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
