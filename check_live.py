import os
import time
import requests

# YouTube Data API Key
API_KEY = 'YOUR_API_KEY'

# YouTube 頻道及其對應的分類
channels = {
    "分類一": {
        "台灣地震監視": "https://www.youtube.com/@台灣地震監視/streams",
        "台視新聞": "https://www.youtube.com/@TTV_NEWS/streams",
        "中視新聞": "https://www.youtube.com/@chinatvnews/streams",
        "中視新聞 HD": "https://www.youtube.com/@twctvnews/streams",
        "華視新聞": "https://www.youtube.com/@CtsTw/streams",
        "民視新聞網": "https://www.youtube.com/@FTV_News/streams",
        # 更多頻道...
    },
    "分類二": {
        "MIT台灣誌": "https://www.youtube.com/@ctvmit/streams",
        "大陸尋奇": "https://www.youtube.com/@ctvchinatv/streams",
        "八大電視娛樂百分百": "https://www.youtube.com/@GTV100ENTERTAINMENT/streams",
        "三立娛樂星聞": "https://www.youtube.com/@star_setn/streams",
        # 更多頻道...
    }
}

# 儲存直播網址的文件夾和檔案路徑
output_folder = '直播網址'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 根據頻道網址抓取直播視頻
def get_live_videos(channel_url):
    # 使用 YouTube Data API 查詢頻道的視頻列表，這裡以 'search' API 為例
    base_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        'key': API_KEY,
        'channelId': channel_url.split('@')[1],  # 提取頻道ID
        'part': 'snippet',
        'eventType': 'live',
        'type': 'video'
    }
    response = requests.get(base_url, params=params)
    return response.json()

# 寫入直播網址到檔案
def write_to_file(category, videos):
    file_path = os.path.join(output_folder, "直播網址.txt")
    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(f"{category},#genre#\n")
        for video in videos:
            title = video['snippet']['title']
            video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
            file.write(f"{title},{video_url}\n")

# 主程式，抓取每個分類的頻道直播視頻
def scrape_live_videos():
    for category, channels_dict in channels.items():
        all_videos = []
        for channel_name, channel_url in channels_dict.items():
            print(f"正在抓取 {channel_name} 的直播視頻...")
            videos = get_live_videos(channel_url)
            if 'items' in videos and videos['items']:
                all_videos.extend(videos['items'])
            else:
                print(f"{channel_name} 沒有找到直播視頻。")
        
        # 如果該分類有抓到視頻，則寫入檔案
        if all_videos:
            write_to_file(category, all_videos)
    
# 定時抓取，這裡設置每 2 小時執行一次
while True:
    scrape_live_videos()
    print("已完成一次抓取，2 小時後再次執行...")
    time.sleep(2 * 60 * 60)  # 2 小時
