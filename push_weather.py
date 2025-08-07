
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
        url = "https://data.moenv.gov.tw/api/v2/aqx_p_432"
        params = {
            "api_key": EPA_API_KEY if EPA_API_KEY else "opendata",
            "limit": 1000,
            "offset": 0,
            # 篩選台北市資料（requests 會自動 URL encode）
            "filters": "county eq 臺北市"
        }
        res = requests.get(url, params=params, timeout=15)

        # --- debug 輸出（會出現在 Actions logs） ---
        print("EPA Request URL:", res.url)
        print("EPA Status code:", res.status_code)
        print("EPA Response preview:", res.text[:800])  # 只顯示前800字

        if res.status_code != 200:
            return f"⚠️ 空氣品質 API 請求失敗，狀態：{res.status_code}"

        # 嘗試解析 JSON
        try:
            data = res.json()
        except ValueError as e:
            return f"⚠️ 空氣品質 JSON 解析失敗：{e}"

        records = data.get("records", [])
        if not records:
            return "⚠️ 空氣品質資料為空（records 空）"

        # 優先找 "中山" 站，找不到就取第一筆
        site = next((r for r in records if r.get("sitename") == "中山"), records[0])
        aqi = site.get("aqi", "N/A")
        status = site.get("status", "N/A")
        pm25 = site.get("pm2.5", site.get("pm25", "N/A"))  # 不同欄位名兼容處理
        sitename = site.get("sitename", "未知站")

        return f"🌫️ 空氣品質（{sitename}）\nAQI：{aqi}（{status}）\nPM2.5：{pm25} µg/m³"

    except Exception as e:
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
