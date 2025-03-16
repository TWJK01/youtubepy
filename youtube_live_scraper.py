import os
import requests
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
CHANNEL_IDS = {
    "華視新聞": "UCDCJyLpbfgeVE9iZiEam-Kg",
    "Muse木棉花-闔家歡": "UCCPYSMEnbeepGM7RU6qxyUA",
    "HOP Sports": "UCEenIlCU009lS0TZ8EKuKMw",
    "超級夜總會": "UCOCcxhYGf0tRhWTL77QQHEA"
}
OUTPUT_FILE = "live_streams.txt"

def get_live_video_ids(channel_id):
    """透過 YouTube Data API 搜尋頻道的直播影片"""
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "id",
        "channelId": channel_id,
        "eventType": "live",  # 只抓直播
        "type": "video",
        "key": YOUTUBE_API_KEY,
        "maxResults": 10
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        logging.error(f"無法獲取 {channel_id} 的直播數據: {response.text}")
        return []
    
    data = response.json()
    return [item["id"]["videoId"] for item in data.get("items", [])]

def filter_live_videos(video_ids):
    """透過 videos API 確認影片的 liveBroadcastContent 狀態"""
    if not video_ids:
        return []

    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "id,snippet,liveStreamingDetails",
        "id": ",".join(video_ids),
        "key": YOUTUBE_API_KEY
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        logging.error(f"無法獲取影片詳細資訊: {response.text}")
        return []
    
    data = response.json()
    live_videos = []
    for item in data.get("items", []):
        if item["snippet"]["liveBroadcastContent"] == "live":
            video_id = item["id"]
            title = item["snippet"]["title"]
            live_videos.append((title, f"https://www.youtube.com/watch?v={video_id}"))
    
    return live_videos

def save_to_file(live_videos):
    """將直播網址寫入檔案"""
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        for title, url in live_videos:
            file.write(f"{title},{url}\n")

def main():
    all_live_videos = []
    
    for name, channel_id in CHANNEL_IDS.items():
        logging.info(f"搜尋 {name} 的直播...")
        video_ids = get_live_video_ids(channel_id)
        live_videos = filter_live_videos(video_ids)

        if live_videos:
            all_live_videos.extend(live_videos)
        else:
            logging.info(f"{name} 目前沒有直播。")

    if all_live_videos:
        save_to_file(all_live_videos)
        logging.info(f"已更新 {OUTPUT_FILE} 檔案，找到 {len(all_live_videos)} 個直播。")
    else:
        open(OUTPUT_FILE, "w").close()  # 清空檔案，代表沒有直播
        logging.info("沒有任何頻道在直播，清空檔案。")

if __name__ == "__main__":
    main()
