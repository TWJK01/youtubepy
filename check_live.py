import requests
import re
import json
import os

API_KEY = os.environ.get("YOUTUBE_API_KEY", "YOUR_API_KEY")

# 分類頻道對應表
CATEGORIES = {
    "分類一,#genre#": {
        "華視新聞": "https://www.youtube.com/@CtsTw/streams",
        "中天新聞CtiNews": "https://www.youtube.com/@中天新聞CtiNews/streams"
    },
    "分類二,#genre#": {
        "MIT台灣誌": "https://www.youtube.com/@ctvmit/streams",
        "大陸尋奇": "https://www.youtube.com/@ctvchinatv/streams"
    },
    "分類三,#genre#": {
        "台視時光機": "https://www.youtube.com/@TTVClassic/streams",
        "中視經典戲劇": "https://www.youtube.com/@ctvdrama_classic/streams"
    },
    "分類四,#genre#": {
        "壹電視NEXT TV": "https://www.youtube.com/@%E5%A3%B9%E9%9B%BB%E8%A6%96NEXTTV/streams",
        "庶民大頭家": "https://www.youtube.com/@庶民大頭家/streams"
    },
    "分類五,#genre#": {
        "YOYOTV": "https://www.youtube.com/@yoyotvebc/streams",
        "momokids親子台": "https://www.youtube.com/@momokidsYT/streams"
    },
    "分類六,#genre#": {
        "愛爾達體育家族": "https://www.youtube.com/@ELTASPORTSHD/streams",
        "緯來體育台": "https://www.youtube.com/@vlsports/streams",
        "HOP Sports": "https://www.youtube.com/@HOPSports/streams"
    },
    "分類七,#genre#": {
        "國會頻道": "https://www.youtube.com/@parliamentarytv/streams"
    }
}

# 儲存分類直播結果
live_results = {category: [] for category in CATEGORIES}

def get_live_video_info(video_id):
    api_url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "id": video_id,
        "part": "snippet,liveStreamingDetails",
        "key": API_KEY
    }
    response = requests.get(api_url, params=params)
    if response.status_code != 200:
        return None
    data = response.json()
    if "items" in data and data["items"]:
        item = data["items"][0]
        if item["snippet"].get("liveBroadcastContent") == "live":
            return item
    return None

def process_channel(category, channel_name, url):
    print(f"處理頻道：{channel_name}")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/115.0 Safari/537.36"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            print(f"取得 {url} 失敗，狀態碼：{resp.status_code}")
            return
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return
    
    html = resp.text
    m = re.search(r"ytInitialData\s*=\s*({.*?});", html)
    if not m:
        print("找不到 ytInitialData")
        return
    
    try:
        data = json.loads(m.group(1))
    except Exception as e:
        print(f"JSON 解析錯誤: {e}")
        return
    
    video_ids = set(re.findall(r'"videoId":"(\w{11})"', html))
    for vid in video_ids:
        info = get_live_video_info(vid)
        if info:
            title = info["snippet"].get("title", "無標題")
            video_url = f"https://www.youtube.com/watch?v={vid}"
            live_results[category].append(f"{channel_name},{video_url}")
            print(f"找到直播：{title} - {video_url}")

def main():
    for category, channels in CATEGORIES.items():
        for channel_name, url in channels.items():
            process_channel(category, channel_name, url)
    
    with open("live_streams.txt", "w", encoding="utf-8") as f:
        for category, results in live_results.items():
            if results:
                f.write(f"{category}\n")
                f.write("\n".join(results) + "\n\n")
    print("更新完成。")

if __name__ == "__main__":
    main()
