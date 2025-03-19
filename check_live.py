#!/usr/bin/env python
import requests
import re
import json
import os
import itertools

# 從 GitHub Secrets 讀取 API Keys
API_KEYS = [
    os.getenv("YOUTUBE_API_KEY_1"),
    os.getenv("YOUTUBE_API_KEY_2"),
]

# 移除 None 值，確保 API_KEYS 都是有效的
API_KEYS = [key for key in API_KEYS if key]

# API Key 輪替迭代器
api_key_cycle = itertools.cycle(API_KEYS)

def get_next_api_key():
    """取得下一組 API Key"""
    return next(api_key_cycle)

# 頻道分類
CATEGORIES = {
    "台灣,#genre#": {
        "台灣地震監視": "https://www.youtube.com/@台灣地震監視/streams"
    },
    "綜藝,#genre#": {
        "MIT台灣誌": "https://www.youtube.com/@ctvmit/streams"
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
    """取得 YouTube 直播資訊，並輪替 API Key"""
    for _ in range(len(API_KEYS)):  # 最多嘗試 5 次
        api_key = get_next_api_key()
        api_url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            "id": video_id,
            "part": "snippet,liveStreamingDetails",
            "key": api_key
        }
        response = requests.get(api_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if "items" in data and len(data["items"]) > 0:
                item = data["items"][0]
                if item["snippet"].get("liveBroadcastContent") == "live":
                    return item
        elif response.status_code == 403:
            print(f"API Key {api_key} 超出配額，切換至下一組...")
    
    print("所有 API Key 皆無法使用。")
    return None

def process_channel(category, channel_name, url):
    """處理指定頻道，尋找直播"""
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
    """主執行函式"""
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
