#!/usr/bin/env python
import requests
import re
import json
import os

# 設定你的 YouTube Data API key
API_KEY = os.environ.get("YOUTUBE_API_KEY", "YOUR_API_KEY")

# 頻道分類
CATEGORIES = {
    "台灣,#genre#": {
        "華視新聞": "https://www.youtube.com/@CtsTw/streams",
    },
    "少兒,#genre#": {
        "Muse木棉花-TW": "https://www.youtube.com/@MuseTW/streams",
        "Muse木棉花-闔家歡": "https://www.youtube.com/@Muse_Family/streams",
    }
}

# 用來儲存直播結果
live_results = {}

def extract_video_ids(data_obj, collected):
    """遞迴提取所有的視頻ID"""
    if isinstance(data_obj, dict):
        if "videoId" in data_obj:
            collected.add(data_obj["videoId"])
        for value in data_obj.values():
            extract_video_ids(value, collected)
    elif isinstance(data_obj, list):
        for item in data_obj:
            extract_video_ids(item, collected)

def get_live_video_info(video_id):
    """通過 YouTube API 獲取直播視頻的詳細信息"""
    api_url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "id": video_id,
        "part": "snippet,liveStreamingDetails",
        "key": API_KEY
    }
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()  # 如果請求不成功，會觸發異常
        data = response.json()
        if "items" in data and len(data["items"]) > 0:
            item = data["items"][0]
            if item["snippet"].get("liveBroadcastContent") == "live":
                return item
    except Exception as e:
        print(f"獲取視頻 {video_id} 信息失敗: {e}")
    return None

def process_channel(category, channel_name, url):
    """處理指定頻道，抓取並儲存所有的直播內容"""
    print(f"處理頻道：{channel_name}")
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            print(f"無法訪問頻道：{channel_name}")
            return
    except Exception as e:
        print(f"請求頻道 {channel_name} 時發生錯誤: {e}")
        return

    html = resp.text
    m = re.search(r"var ytInitialData = ({.*?});", html)
    if not m:
        print(f"無法提取數據：{channel_name}")
        return

    try:
        data = json.loads(m.group(1))
    except Exception as e:
        print(f"解析數據時出錯：{channel_name}, 錯誤信息：{e}")
        return

    video_ids = set()
    extract_video_ids(data, video_ids)

    # 優化提取多個頁面視頻的方式，保證不漏掉直播
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
