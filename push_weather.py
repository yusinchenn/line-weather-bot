import requests
import os
from linebot import LineBotApi
from linebot.models import TextSendMessage

# 讀取 Secrets
LINE_TOKEN = os.getenv("LINE_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")
CWB_API_KEY = os.getenv("CWB_API_KEY")

line_bot_api = LineBotApi(LINE_TOKEN)

# 天氣資訊
def get_weather():
    url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"
    params = {
        "Authorization": CWB_API_KEY,
        "locationName": "台北市"
    }
    r = requests.get(url, params=params).json()
    elements = r['records']['location'][0]['weatherElement']
    weather = elements[0]['time'][0]['parameter']['parameterName']
    rain = elements[1]['time'][0]['parameter']['parameterName']
    temp_min = elements[2]['time'][0]['parameter']['parameterName']
    temp_max = elements[4]['time'][0]['parameter']['parameterName']

    return f"☁️ 台北天氣：{weather}\n🌡️ 溫度：{temp_min}°C ~ {temp_max}°C\n🌧️ 降雨機率：{rain}%"

# 空氣品質（AQI）
def get_air_quality():
    url = "https://data.moenv.gov.tw/api/v2/aqx_p_432?offset=0&limit=1000&api_key=opendata"
    r = requests.get(url).json()
    for site in r['records']:
        if site['county'] == "台北市" and site['sitename'] == "中山":
            aqi = site['aqi']
            status = site['status']
            pm25 = site['pm2.5']
            return f"🌫️ 空氣品質（中山站）\nAQI：{aqi}（{status}）\nPM2.5：{pm25} µg/m³"
    return "❗ 無法取得空氣品質資料"

# 推播
def push_report():
    weather = get_weather()
    air = get_air_quality()
    message = f"{weather}\n\n{air}"
    line_bot_api.push_message(LINE_USER_ID, TextSendMessage(text=message))

if __name__ == "__main__":
    push_report()
