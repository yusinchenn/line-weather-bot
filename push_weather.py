
import os
import requests
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
    try:
        url = f"https://data.moenv.gov.tw/api/v2/aqx_p_432?api_key={EPA_API_KEY}&limit=10&offset=0&filters=county,eq,臺北市|sitename,ne,中山"
        res = requests.get(url)  # 先取得回應物件，不要直接 .json()

        # 【除錯步驟】印出 HTTP 狀態碼與原始回應內容
        print(f"空氣品質 API 狀態碼：{res.status_code}")
        print(f"空氣品質 API 原始回應：\n{res.text}")

        # 先確認請求成功 (狀態碼 200)，再進行 JSON 解析
        if res.status_code == 200:
            data = res.json()
            # 檢查 'records' 是否存在且不為空
            if data.get('records') and len(data['records']) > 0:
                site = data['records'][0]
                aqi = site['aqi']
                status = site['status']
                return f"🌫️ 空氣品質指數（AQI）：{aqi}（{status}）"
            else:
                return "⚠️ 空氣品質資料取得成功，但內容為空。"
        else:
            return f"⚠️ 空氣品質 API 請求失敗，狀態碼：{res.status_code}"

    except Exception as e:
        # 捕捉其他可能的錯誤，例如網路連線問題
        return f"⚠️ 空氣品質資料處理時發生錯誤：{e}"

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
