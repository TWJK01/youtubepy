#!/usr/bin/env python
import requests
import re
import json
import os
import itertools

# 設定你的多組 YouTube Data API keys
API_KEYS = [
    "YOUR_API_KEY_1",
    "YOUR_API_KEY_2"  # 你可以添加更多的 API keys
]

# 創建一個輪替器來處理多組 API keys
api_key_cycle = itertools.cycle(API_KEYS)

# 頻道分類
CATEGORIES = {
    "台灣,#genre#": {
        "華視新聞": "https://www.youtube.com/@CtsTw/streams",
    },
    "少兒,#genre#": {
        "Muse木棉花-闔家歡": "https://www.youtube.com/@Muse_Family/streams"        
    }
}

# 用來儲存直播結果
live_results = {}

def extract_video_ids(data_obj, collected):
    if isinstance(data_obj, dict):
        if "videoId" in data_obj:
            collected.add(data_obj["videoId"])
        for value in data_obj.values():
            extract_video_ids(value, collected)
    elif isinstance(data_obj, list):
        for item in data_obj:
            extract_video_ids(item, collected)

def get_live_video_info(video_id):
    api_url = "https://www.googleapis.com/youtube/v3/videos"
    # 使用輪替器獲取當前 API key
    api_key = next(api_key_cycle)
    
    params = {
        "id": video_id,
        "part": "snippet,liveStreamingDetails",
        "key": api_key
    }
    
    response = requests.get(api_url, params=params)
    if response.status_code != 200:
        print(f"API 請求失敗，狀態碼: {response.status_code}")
        return None
    
    data = response.json()
    if "items" in data and len(data["items"]) > 0:
        item = data["items"][0]
        if item["snippet"].get("liveBroadcastContent") == "live":
            return item
    return None

def process_channel(category, channel_name, url):
    print(f"處理頻道：{channel_name}")
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return
    except Exception:
        return

    html = resp.text
    m = re.search(r"var ytInitialData = ({.*?});", html)
    if not m:
        return

    try:
        data = json.loads(m.group(1))
    except Exception:
        return

    video_ids = set()
    extract_video_ids(data, video_ids)

    for vid in video_ids:
        info = get_live_video_info(vid)
        if info:
            title = info["snippet"].get("title", "無標題")
            video_url = f"https://www.youtube.com/watch?v={vid}"
            if category not in live_results:
                live_results[category] = []
            live_results[category].append(f"{title},{video_url}")
            print(f"找到直播：{title} - {video_url}")

def main():
    for category, channels in CATEGORIES.items():
        for channel_name, url in channels.items():
            process_channel(category, channel_name, url)

    with open("live_streams.txt", "w", encoding="utf-8") as f:
        for category, streams in live_results.items():
            f.write(category + "\n")
            for line in streams:
                f.write(line + "\n")
            f.write("\n")
    print("更新完成。")

if __name__ == "__main__":
    main()
