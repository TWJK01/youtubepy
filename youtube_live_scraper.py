import os
import requests

def get_live_videos(api_key, channel_ids):
    base_url = "https://www.googleapis.com/youtube/v3/search"
    live_videos = []
    
    for name, channel_id in channel_ids.items():
        params = {
            "part": "snippet",
            "channelId": channel_id,
            "eventType": "live",
            "type": "video",
            "key": api_key
        }
        
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            for item in data.get("items", []):
                video_id = item["id"]["videoId"]
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                live_videos.append(f"{name},{video_url}")
    
    return live_videos

def save_to_file(live_videos, filename="live_streams.txt"):
    with open(filename, "w", encoding="utf-8") as file:
        file.write("\n".join(live_videos))

def main():
    api_key = os.getenv("YOUTUBE_API_KEY")
    channel_ids = {
        "華視新聞": "UCDCJyLpbfgeVE9iZiEam-Kg",
        "Muse木棉花-闔家歡": "UCCPYSMEnbeepGM7RU6qxyUA",
        "HOP Sports": "UCEenIlCU009lS0TZ8EKuKMw",
        "超級夜總會": "UCOCcxhYGf0tRhWTL77QQHEA"
    }
    
    live_videos = get_live_videos(api_key, channel_ids)
    if live_videos:
        save_to_file(live_videos)
    else:
        open("live_streams.txt", "w").close()  # 清空檔案，表示無直播

if __name__ == "__main__":
    main()
