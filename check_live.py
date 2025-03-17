import requests
import re
import json
import os
from dotenv import load_dotenv

# 加載 .env 檔案中的 API_KEY
load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY", "YOUR_API_KEY")

# 頻道分類與直播頁面 URL
CATEGORIES = {
    "台灣,#genre#": {
        "華視新聞": "https://www.youtube.com/@CtsTw/streams",
    },
    "少兒,#genre#": {
        "Muse木棉花-TW": "https://www.youtube.com/@MuseTW/streams",
        "Muse木棉花-闔家歡": "https://www.youtube.com/@Muse_Family/streams"
    }
}

# 儲存直播結果
live_results = {}

def search_live_videos(channel_id):
    """使用 YouTube Data API 搜尋頻道的直播影片"""
    api_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "channelId": channel_id,
        "eventType": "live",
        "type": "video",
        "key": API_KEY
    }
    response = requests.get(api_url, params=params)
    if response.status_code != 200:
        print(f"[錯誤] API 請求失敗: {response.status_code}")
        return []
    data = response.json()
    return [(item["id"]["videoId"], item["snippet"]["title"]) for item in data.get("items", [])]

def get_channel_id(channel_url):
    """解析 YouTube 頻道 ID"""
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(channel_url, headers=headers, timeout=10)
        if resp.status_code != 200:
            print(f"[錯誤] 無法訪問 {channel_url}")
            return None
    except Exception as e:
        print(f"[錯誤] {channel_url} 請求失敗: {e}")
        return None
    
    match = re.search(r"channel/([\w-]+)", resp.text)
    return match.group(1) if match else None

def process_channel(category, channel_name, url):
    print(f"處理頻道：{channel_name}")
    channel_id = get_channel_id(url)
    if not channel_id:
        return
    
    live_videos = search_live_videos(channel_id)
    if not live_videos:
        print(f"[訊息] {channel_name} 沒有找到直播影片")
        return
    
    if category not in live_results:
        live_results[category] = []
    
    for vid, title in live_videos:
        video_url = f"https://www.youtube.com/watch?v={vid}"
        live_results[category].append(f"{title},{video_url}")
        print(f"找到直播：{title} - {video_url}")

def main():
    for category, channels in CATEGORIES.items():
        for channel_name, url in channels.items():
            process_channel(category, channel_name, url)
    
    # 存為 JSON
    with open("live_streams.json", "w", encoding="utf-8") as f:
        json.dump(live_results, f, ensure_ascii=False, indent=4)
    
    # 存為 TXT
    with open("live_streams.txt", "w", encoding="utf-8") as f:
        for category, streams in live_results.items():
            f.write(category + "\n")
            for line in streams:
                f.write(line + "\n")
            f.write("\n")
    print("更新完成。")

if __name__ == "__main__":
    main()
