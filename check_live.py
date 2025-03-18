#!/usr/bin/env python
import requests
import json
import os
import itertools
import re

# 輪流使用 API Key，防止達到 YouTube API 限制
API_KEYS = [
    os.getenv("YOUTUBE_API_KEY_1"),
    os.getenv("YOUTUBE_API_KEY_2"),
]

api_key_cycle = itertools.cycle(API_KEYS)

def get_next_api_key():
    """取得下一個 API Key
    """
    return next(api_key_cycle)

# 定義要爬取的 YouTube 頻道直播頁面
CATEGORIES = {
    "台灣,#genre#": {
        "8world": "https://www.youtube.com/@8worldSG/streams",
        "台視": "https://www.youtube.com/watch?v=uDqQo8a7Xmk&rco=1&ab_channel=TTVLIVE%E5%8F%B0%E8%A6%96%E7%9B%B4%E6%92%AD"
    },
    "綜藝,#genre#": {
        "戲說台灣": "https://www.youtube.com/@TWStoryTV/streams"	
    },
}

# 用來存儲直播結果
live_results = {}

def extract_video_ids(data_obj, collected):
    """解析 YouTube 頁面 JSON，提取 videoId
    """
    if isinstance(data_obj, dict):
        if "videoId" in data_obj:
            collected.add(data_obj["videoId"])
        for value in data_obj.values():
            extract_video_ids(value, collected)
    elif isinstance(data_obj, list):
        for item in data_obj:
            extract_video_ids(item, collected)

def get_live_video_info(video_id):
    """查詢 YouTube API 確認直播狀態
    """
    api_key = get_next_api_key()
    api_url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "id": video_id,
        "part": "snippet,liveStreamingDetails",
        "key": api_key
    }
    response = requests.get(api_url, params=params)
    if response.status_code != 200:
        return None
    data = response.json()
    if "items" in data and len(data["items"]) > 0:
        item = data["items"][0]
        if item["snippet"].get("liveBroadcastContent") == "live":
            return item
    return None

def process_channel(category, channel_name, url):
    """處理單一 YouTube 頻道頁面
    """
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
    """執行主程序，遍歷所有頻道
    """
    for category, channels in CATEGORIES.items():
        for channel_name, url in channels.items():
            process_channel(category, channel_name, url)

    with open("live_streams.txt", "w", encoding="utf-8") as f:
        for category, streams in live_results.items():
            f.write(category + "\n")
            for line in streams:
                f.write(line + "\n")
            f.write("\n")

    # 自動提交更新
    os.system("git config --global user.name 'github-actions[bot]'")
    os.system("git config --global user.email 'github-actions[bot]@users.noreply.github.com'")
    os.system("git pull --rebase origin main || git reset --hard origin/main")
    os.system("git add live_streams.txt")
    os.system("git commit -m '更新直播清單'")
    os.system("git push --force-with-lease")
    
    print("更新完成。")

if __name__ == "__main__":
    main()
