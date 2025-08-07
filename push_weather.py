
import os
import requests
from linebot import LineBotApi
from linebot.models import TextSendMessage

LINE_TOKEN = os.getenv('LINE_TOKEN')
CWB_API_KEY = os.getenv('CWB_API_KEY')
EPA_API_KEY = os.getenv('EPA_API_KEY')
line_bot_api = LineBotApi(LINE_TOKEN)

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

def get_air_quality():
    try:
        url = f"https://data.moenv.gov.tw/api/v2/aqx_p_432?offset=0&limit=1&api_key={EPA_API_KEY}&filters=county eq 臺北市"
        res = requests.get(url).json()
        site = res['records'][0]
        aqi = site['aqi']
        status = site['status']
        return f"🌫️ 空氣品質指數（AQI）：{aqi}（{status}）"
    except Exception as e:
        return f"⚠️ 空氣品質資料取得失敗：{e}"

def main():
    weather = get_weather()
    air = get_air_quality()
    message = f"{weather}\n{air}"
    line_bot_api.broadcast(TextSendMessage(text=message))

if __name__ == "__main__":
    main()
