
import os
import requests
from urllib.parse import quote
from linebot import LineBotApi
from linebot.models import TextSendMessage

LINE_TOKEN = os.getenv('LINE_TOKEN')
CWB_API_KEY = os.getenv('CWB_API_KEY')
EPA_API_KEY = os.getenv('EPA_API_KEY')
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

def get_air_quality():
    siteid = 12  # URL encode 中文
    url = (
        f"https://data.moenv.gov.tw/api/v2/aqx_p_432"
        f"?format=JSON&offset=0&limit=1&api_key={EPA_API_KEY}"
    )

    res = requests.get(url)
    print("空氣品質 API 狀態碼：", res.status_code)
    print("空氣品質 API 原始回應：", res.text)  # Debug 用

    res.raise_for_status()
    data = res.json()

    if 'records' not in data or not data['records']:
        return "⚠️ 無法取得空氣品質資料"

    site = data['records'][0]
    aqi = site.get('aqi', 'N/A')
    status = site.get('status', '未知')
    return f"🌫️ 空氣品質指數（AQI）：{aqi}（{status}）"


def main():
    weather = get_weather()
    air = get_air_quality() # 使用上面修正過的函式
    message = f"{weather}\n{air}"

    # --- LINE SDK v3 寫法 ---
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
