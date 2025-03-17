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
        "台灣地震監視": "https://www.youtube.com/@台灣地震監視/streams",
        "台視新聞": "https://www.youtube.com/@TTV_NEWS/streams",
        "中視新聞": "https://www.youtube.com/@chinatvnews/streams",
        "中視新聞 HD": "https://www.youtube.com/@twctvnews/streams",
        "華視新聞": "https://www.youtube.com/@CtsTw/streams",
        "民視新聞網": "https://www.youtube.com/@FTV_News/streams",
        "公視": "https://www.youtube.com/@ptslivestream/streams",
        "公視新聞網": "https://www.youtube.com/@PNNPTS/streams",
        "公視台語台": "https://www.youtube.com/@ptstaigitai/streams",
        "大愛電視": "https://www.youtube.com/@DaAiVideo/streams",
        "鏡新聞": "https://www.youtube.com/@mnews-tw/streams",
        "東森新聞": "https://www.youtube.com/@newsebc/streams",	
        "三立iNEWS": "https://www.youtube.com/@setinews/streams",
        "三立LIVE新聞": "https://www.youtube.com/@setnews/streams",
        "中天新聞CtiNews": "https://www.youtube.com/@中天新聞CtiNews/streams",
        "中天電視CtiTv": "https://www.youtube.com/@中天電視CtiTv/streams",
        "中天亞洲台": "https://www.youtube.com/@中天亞洲台CtiAsia/streams",
        "CTI+ | 中天2台": "https://www.youtube.com/@中天2台ctiplusnews/streams",	
        "TVBS NEWS": "https://www.youtube.com/@TVBSNEWS01/streams",
        "Focus全球新聞": "https://www.youtube.com/@tvbsfocus/streams",	
        "寰宇新聞": "https://www.youtube.com/@globalnewstw/streams",
        "udn video": "https://www.youtube.com/@udn-video/streams",
        "CNEWS匯流新聞網": "https://www.youtube.com/@CNEWS/streams",	
        "新唐人亞太電視台": "https://www.youtube.com/@NTDAPTV/streams",
        "原視新聞網 TITV News": "https://www.youtube.com/@TITVNews16/streams",	
        "三大一台": "https://www.youtube.com/@SDTV55ch/streams",	
        "中天財經頻道": "https://www.youtube.com/@中天財經頻道CtiFinance/streams",	
        "東森財經股市": "https://www.youtube.com/@57ETFN/streams",	
        "寰宇財經新聞": "https://www.youtube.com/@globalmoneytv/streams",
        "非凡電視": "https://www.youtube.com/@ustv/streams",
        "非凡商業台": "https://www.youtube.com/@ustvbiz/streams",	
        "運通財經台": "https://www.youtube.com/@EFTV01/streams",
        "全球財經台2": "https://www.youtube.com/@全球財經台2/streams",	
        "AI主播倪珍Nikki 播新聞": "https://www.youtube.com/@NOWnews-sp2di/streams",
        "BNE TV - 新西兰中文国际频道": "https://www.youtube.com/@BNETVNZ/streams",	
        "POP Radio聯播網": "https://www.youtube.com/@917POPRadio/streams",
        "Eight FM": "https://www.youtube.com/@eight-audio/streams",	
        "鳳凰衛視PhoenixTV": "https://www.youtube.com/@phoenixtvhk/streams",
        "鳳凰資訊 PhoenixTVNews": "https://www.youtube.com/@phoenixtvnews7060/streams",	
        "CCTV中文": "https://www.youtube.com/@LiveNow24H/streams",
        "8world": "https://www.youtube.com/@8worldSG/streams"
    },
    "綜藝,#genre#": {
        "MIT台灣誌": "https://www.youtube.com/@ctvmit/streams",
        "大陸尋奇": "https://www.youtube.com/@ctvchinatv/streams",	
        "八大電視娛樂百分百": "https://www.youtube.com/@GTV100ENTERTAINMENT/streams",
        "三立娛樂星聞": "https://www.youtube.com/@star_setn/streams",	
        "中視經典綜藝": "https://www.youtube.com/@ctvent_classic/streams",
        "小姐不熙娣": "https://www.youtube.com/@deegirlstalk/streams",
        "木曜4超玩": "https://www.youtube.com/@Muyao4/streams",	
        "華視綜藝頻道": "https://www.youtube.com/@CTSSHOW/streams",
        "綜藝大熱門": "https://www.youtube.com/@HotDoorNight/streams",
        "綜藝玩很大": "https://www.youtube.com/@Mr.Player/streams",	
        "11點熱吵店": "https://www.youtube.com/@chopchopshow/streams",
        "飢餓遊戲": "https://www.youtube.com/@HungerGames123/streams",	
        "豬哥會社": "https://www.youtube.com/@FTV_ZhuGeClub/streams",
        "百變智多星": "https://www.youtube.com/@百變智多星/streams",	
        "東森綜合台": "https://www.youtube.com/@中天娛樂CtiEntertainment/streams",
        "中天娛樂頻道": "https://www.youtube.com/@ettv32/streams",	
        "WeTV 綜藝經典": "https://www.youtube.com/@WeTV-ClassicVariety/streams",	
        "57怪奇物語": "https://www.youtube.com/@57StrangerThings/streams",
        "命運好好玩": "https://www.youtube.com/@eravideo004/streams",	
        "TVBS娛樂頭條": "https://www.youtube.com/@tvbsenews/streams",	
        "台灣啟示錄": "https://www.youtube.com/@ebcapocalypse/streams",
        "緯來日本台": "https://www.youtube.com/@VideolandJapan/streams",
        "我愛小明星大跟班": "https://www.youtube.com/@我愛小明星大跟班/streams",
        "204檔案": "https://www.youtube.com/@204/streams",
        "WTO姐妹會": "https://www.youtube.com/@WTOSS/streams",	
        "好看娛樂": "https://www.youtube.com/@好看娛樂/streams",
        "超級夜總會": "https://www.youtube.com/@SuperNightClubCH29/videos",	
        "TVBS女人我最大": "https://www.youtube.com/@tvbsqueen/streams",
        "型男大主廚": "https://www.youtube.com/@twcookingshow/streams",	
        "非凡大探索": "https://www.youtube.com/@ustvfoody/streams",
        "你好, 星期六 Hello Saturday Official": "https://www.youtube.com/@HelloSaturdayOfficial/streams",	
        "BIF相信未來 官方頻道": "https://www.youtube.com/@BelieveinfutureTV/streams",
        "原視 TITV+": "https://www.youtube.com/@titv8932/videos",
        "Taste The World": "https://www.youtube.com/@TasteTheWorld66/streams",
        "公共電視-我們的島": "https://www.youtube.com/@ourislandTAIWAN/streams",	
        "戲說台灣": "https://www.youtube.com/@TWStoryTV/streams"	
    },
    "影劇,#genre#": {
        "CCTV纪录": "https://www.youtube.com/@CCTVDocumentary/streams",	
        "台視時光機": "https://www.youtube.com/@TTVClassic/streams",
        "中視經典戲劇": "https://www.youtube.com/@ctvdrama_classic/streams",
        "華視戲劇頻道": "https://www.youtube.com/@cts_drama/streams",
        "民視戲劇館": "https://www.youtube.com/@FTVDRAMA/streams",
        "四季線上4gTV": "https://www.youtube.com/@4gTV_online/streams",	
        "三立電視 SET TV": "https://www.youtube.com/@SETTV/streams",
        "三立華劇 SET Drama": "https://www.youtube.com/@SETdrama/streams",
        "三立台劇 SET Drama": "https://www.youtube.com/@setdramatw/streams",	
        "終極系列": "https://www.youtube.com/@KOONERETURN/streams",
        "TVBS劇在一起": "https://www.youtube.com/@tvbsdrama/streams",
        "TVBS戲劇-女兵日記 女力報到": "https://www.youtube.com/@tvbs-1587/streams",	
        "八大劇樂部": "https://www.youtube.com/@gtv-drama/streams",
        "GTV DRAMA English": "https://www.youtube.com/@gtvdramaenglish/streams",
        "萌萌愛追劇": "https://www.youtube.com/@mengmengaizhuijuminidrama/streams",	
        "龍華電視": "https://www.youtube.com/@ltv_tw/streams",	
        "愛爾達綜合台": "https://www.youtube.com/@ELTAWORLD/streams",
        "愛爾達影劇台": "https://www.youtube.com/@eltadrama/streams",
        "VBL Series": "https://www.youtube.com/@variety_between_love/streams",	
        "精选大剧": "https://www.youtube.com/@精选大剧/streams",	
        "百纳经典独播剧场": "https://www.youtube.com/@BainationTVSeriesOfficial/streams",
        "华录百納熱播劇場": "https://www.youtube.com/@Baination/streams",	
        "iQIYI 爱奇艺": "https://www.youtube.com/@iQIYIofficial/streams",
        "iQIYI Indonesia": "https://www.youtube.com/@iQIYIIndonesia/streams",	
        "MangoTV Shorts": "https://www.youtube.com/@MangoTVShorts/streams",
        "芒果TV古裝劇場": "https://www.youtube.com/@TVMangoTVCostume-yw1hj/streams",	
        "芒果TV青春剧场": "https://www.youtube.com/@MangoTVDramaOfficial/streams",	
        "芒果TV季风频道": "https://www.youtube.com/@MangoMonsoon/streams",	
        "芒果TV推理宇宙": "https://www.youtube.com/@MangoTV-Mystery/streams",
        "芒果TV大電影劇場": "https://www.youtube.com/@MangoC-TheatreChannel/streams",
        "芒果TV心动": "https://www.youtube.com/@MangoTVSparkle/streams",	
        "CCTV电视剧": "https://www.youtube.com/@CCTVDrama/streams",	
        "SMG上海电视台官方频道": "https://www.youtube.com/@SMG-Official/streams",
        "SMG上海东方卫视欢乐频道": "https://www.youtube.com/@SMG-Comedy/streams",
        "安徽衛視官方頻道": "https://www.youtube.com/@chinaanhuitvofficialchanne8354/streams",	
        "中国东方卫视官方频道": "https://www.youtube.com/@SMGDragonTV/streams",
        "北京广播电视台官方频道": "https://www.youtube.com/@Brtvofficialchannel/streams",
        "陕西广播电视台官方频道": "https://www.youtube.com/@chinashaanxitvofficialchan2836/streams",
        "贵州卫视官方频道": "https://www.youtube.com/@gztvofficial/streams",	
        "SMG音乐频道": "https://www.youtube.com/@SMGMusic/streams"				
    },
    "政論,#genre#": {
        "壹電視NEXT TV": "https://www.youtube.com/@%E5%A3%B9%E9%9B%BB%E8%A6%96NEXTTV/streams",
        "庶民大頭家": "https://www.youtube.com/@庶民大頭家/streams",
        "TVBS 優選頻道": "https://www.youtube.com/@tvbschannel/streams",
        "街頭麥克風": "https://www.youtube.com/@street-mic/streams",
        "全球大視野": "https://www.youtube.com/@全球大視野Global_Vision/streams",	
        "民視讚夯": "https://www.youtube.com/@FTV_Forum/streams",
        "新台派上線": "https://www.youtube.com/@NewTaiwanonline/streams",	
        "94要客訴": "https://www.youtube.com/@94politics/streams",	
        "大新聞大爆卦": "https://www.youtube.com/@大新聞大爆卦HotNewsTalk/streams",	
        "新聞大白話": "https://www.youtube.com/@tvbstalk/streams",
        "國民大會": "https://www.youtube.com/@tvbscitizenclub/streams",	
        "中時新聞網": "https://www.youtube.com/@ChinaTimes/streams",
        "新聞挖挖哇！": "https://www.youtube.com/@newswawawa/streams",	
        "前進新台灣": "https://www.youtube.com/@SETTaiwanGo/streams",
        "哏傳媒": "https://www.youtube.com/@funseeTW/streams",	
        "57爆新聞": "https://www.youtube.com/@57BreakingNews/streams",
        "關鍵時刻": "https://www.youtube.com/@ebcCTime/streams",
		"少康戰情室": "https://www.youtube.com/@tvbssituationroom/streams",
        "文茜的世界周報": "https://www.youtube.com/@tvbssisysworldnews/streams", 
        "金臨天下": "https://www.youtube.com/@tvbsmoney/streams"				
    },
    "少兒,#genre#": {
        "YOYOTV": "https://www.youtube.com/@yoyotvebc/streams",
        "momokids親子台": "https://www.youtube.com/@momokidsYT/streams",
        "Bebefinn 繁體中文 - 兒歌": "https://www.youtube.com/@Bebefinn繁體中文/streams",
        "寶貝多米-兒歌童謠-卡通動畫-經典故事": "https://www.youtube.com/@Domikids_CN/streams",
        "會說話的湯姆貓家族": "https://www.youtube.com/@TalkingFriendsCN/streams",
        "瑪莎與熊": "https://www.youtube.com/@MashaBearTAIWAN/streams",	
        "碰碰狐 鯊魚寶寶": "https://www.youtube.com/@Pinkfong繁體中文/streams",
        "碰碰狐 Pinkfong Baby Shark 儿歌·故事": "https://www.youtube.com/@Pinkfong简体中文/streams",	
        "寶寶巴士": "https://www.youtube.com/@BabyBusTC/streams",
        "Miliki Family - 繁體中文 - 兒歌": "https://www.youtube.com/@MilikiFamily_Chinese/streams",	
        "貝樂虎-幼兒動畫-早教启蒙": "https://www.youtube.com/@BarryTiger_Education_CN/streams",	
        "貝樂虎兒歌-童謠歌曲": "https://www.youtube.com/@barrytiger_kidssongs/streams",
        "貝樂虎-兒歌童謠-卡通動畫-經典故事": "https://www.youtube.com/@barrytiger_zh/streams",
        "小猪佩奇": "https://www.youtube.com/@PeppaPigChineseOfficial/streams",
        "Kids Songs - Giligilis": "https://www.youtube.com/@KidsSongs6868/streams",
        "超級汽車-卡通動畫": "https://www.youtube.com/@Supercar_Cartoon/streams",	
        "神奇鸡仔": "https://www.youtube.com/@como_cn/streams",
        "朱妮托尼 - 动画儿歌": "https://www.youtube.com/@JunyTonyCN/streams",	
        "會說話的湯姆貓家族": "https://www.youtube.com/@TalkingFriendsCN/streams",
        "Muse木棉花-TW": "https://www.youtube.com/@MuseTW/streams",	
        "Muse木棉花-闔家歡": "https://www.youtube.com/@Muse_Family/streams",
        "嗶哩嗶哩動畫Anime Made By Bilibili": "https://www.youtube.com/@MadeByBilibili/streams",	
        "回歸線娛樂": "https://www.youtube.com/@tropicsanime/streams",
        "愛奇藝國漫": "https://www.youtube.com/@iQIYIAnimation/streams",	
        "超人官方 YouTube 粵語頻道": "https://www.youtube.com/@ultraman_cantonese_official/streams"				
    },
    "體育,#genre#": {
        "愛爾達體育家族": "https://www.youtube.com/@ELTASPORTSHD/streams",
        "緯來體育台": "https://www.youtube.com/@vlsports/streams",
        "庫泊運動賽事": "https://www.youtube.com/@coopersport-live/streams",	
        "智林體育台": "https://www.youtube.com/@oursport_tv1/streams",
        "博斯體育台": "https://www.youtube.com/@Sportcasttw/streams",	
        "HOP Sports": "https://www.youtube.com/@HOPSports/streams",
        "DAZN 台灣": "https://www.youtube.com/@DAZNTaiwan/streams",	
        "動滋Sports": "https://www.youtube.com/@Sport_sa_taiwan/streams",
        "GoHoops": "https://www.youtube.com/@GoHoops/streams",
        "P.LEAGUE+": "https://www.youtube.com/@PLEAGUEofficial/streams",	
        "日本B聯盟": "https://www.youtube.com/@b.leagueinternational/streams",	
        "WWE": "https://www.youtube.com/@WWE/streams"		
    },
	"購物,#genre#": {
        "momo購物一台": "https://www.youtube.com/@momoch4812/streams",
		"momo購物二台": "https://www.youtube.com/@momoch3571/streams",
		"ViVa TV美好家庭購物": "https://www.youtube.com/@ViVaTVtw/streams",
		"Live東森購物台": "https://www.youtube.com/@HotsaleTV/streams"		
    },
    "國會,#genre#": {
        "國會頻道": "https://www.youtube.com/@parliamentarytv/streams"
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
    params = {
        "id": video_id,
        "part": "snippet,liveStreamingDetails",
        "key": API_KEY
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
