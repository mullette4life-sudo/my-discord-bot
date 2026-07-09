import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone

# =========================================================================
# [설정 부분] 새 곡이 나오면 곡 태그와 주소 맨 뒤 숫자(ID)만 수정하세요!
# =========================================================================
TRACK_TAGS = "Ice Cream #IceCream 실시간 순위"

TRACK_IDS = {
    "melon_realtime": "602450078",   # 멜론 실시간 트렌드 ID
    "melon_top100":   "602450078",   # 멜론 Top 100 ID
    "melon_hot100":   "602450078",   # 멜론 Hot 100 ID
    "flo_chart":      "595700972",   # 플로 차트 ID
    "genie_realtime": "115753952",   # 지니 실시간 ID
    "bugs_realtime":  "6488138"      # 벅스 실시간 ID
}

# 디스코드 웹훅 URL
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1524901754674872564/TXclUDd3qlaRFtMQoqCtCQhMOteXphf9_3wPi4DAKa0K13GjsKeomVBqNf92YL9touW0"
# =========================================================================

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_kst_now():
    """서버 위치와 상관없이 무조건 한국 시간(KST)을 반환하는 함수"""
    kst_zone = timezone(timedelta(hours=9))
    return datetime.now(kst_zone)
    
def parse_guyso_rank(url):
    """가이섬 사이트에서 '한국 날짜'의 '한국 시간' 순위를 정확히 긁어오는 함수"""
    try:
        res = requests.get(url, headers=HEADERS)
        if res.status_code != 200:
            return "미진입🚨"
            
        soup = BeautifulSoup(res.text, "html.parser")
        
        # 💡 [수정] 무조건 한국 시간(KST) 기준으로 계산합니다.
        kst_now = get_kst_now()
        today_str = kst_now.strftime("%Y%m%d")
        current_hour = kst_now.hour
        target_class = f"thour{current_hour}"
        
        all_rows = soup.find_all("tr")
        target_row = None
        
        for row in all_rows:
            first_cell = row.find("td")
            if first_cell and today_str in first_cell.text:
                target_row = row
                break
        
        if target_row:
            rank_element = target_row.find("td", class_=target_class)
            if rank_element:
                rank_text = rank_element.text.strip()
                if not rank_text or "background-color: black" in str(rank_element) or "background: black" in str(rank_element):
                    return "미진입🚨"
                return f"{rank_text}위"
        
        return "미진입🚨"
    except:
        return "미진입🚨"
        
def main():
    # 💡 [수정] 디스코드용 시간 포맷팅도 한국 시간 기준으로 처리합니다.
    kst_now = get_kst_now()
    current_time_str = kst_now.strftime("%m/%d %H시")
    
    # 각 차트별 크롤링 (ID가 없으면 미진입 처리)
    m_rt = parse_guyso_rank(f"https://xn--o39an51b2re.com/chart/melon/realtime/trend/ranking/{TRACK_IDS['melon_realtime']}") if TRACK_IDS['melon_realtime'] else "미진입🚨"
    m_top = parse_guyso_rank(f"https://xn--o39an51b2re.com/chart/melon/top100/trend/ranking/{TRACK_IDS['melon_top100']}") if TRACK_IDS['melon_top100'] else "미진입🚨"
    m_hot = parse_guyso_rank(f"https://xn--o39an51b2re.com/chart/melon/hot100-d30/trend/ranking/{TRACK_IDS['melon_hot100']}") if TRACK_IDS['melon_hot100'] else "미진입🚨"
    flo = parse_guyso_rank(f"https://xn--o39an51b2re.com/chart/flo/24hour/trend/ranking/{TRACK_IDS['flo_chart']}") if TRACK_IDS['flo_chart'] else "미진입🚨"
    genie = parse_guyso_rank(f"https://xn--o39an51b2re.com/chart/genie/realtime/trend/ranking/{TRACK_IDS['genie_realtime']}") if TRACK_IDS['genie_realtime'] else "미진입🚨"
    bugs = parse_guyso_rank(f"https://xn--o39an51b2re.com/chart/bugs/realtime/trend/ranking/{TRACK_IDS['bugs_realtime']}") if TRACK_IDS['bugs_realtime'] else "미진입🚨"

    # 메시지 조립
    message_content = (
        f"{current_time_str}\n"
        f"{TRACK_TAGS}\n"
        f"멜론 실시간 {m_rt}\n"
        f"멜론 TOP100 {m_top}\n"
        f"멜론 HOT100 {m_hot}\n"
        f"플로 {flo}\n"
        f"지니 {genie}\n"
        f"벅스 {bugs}"
    )
    
    payload = {"content": message_content}
    requests.post(DISCORD_WEBHOOK_URL, json=payload)

if __name__ == "__main__":
    main()
