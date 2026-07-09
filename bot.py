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

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1524901754674872564/TXclUDd3qlaRFtMQoqCtCQhMOteXphf9_3wPi4DAKa0K13GjsKeomVBqNf92YL9touW0"
# =========================================================================

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_kst_now():
    """서버 위치와 상관없이 무조건 한국 시간(KST)을 반환하는 함수"""
    kst_zone = timezone(timedelta(hours=9))
    return datetime.now(kst_zone)

def check_chart_out(element):
    """태그가 비어있거나 검은색(차트아웃)인지 판별하는 함수"""
    if not element:
        return True
    text = element.text.strip()
    if not text or "background-color: black" in str(element) or "background: black" in str(element):
        return True
    return False

def calculate_change(current_url):
    """현재 순위와 직전 순위를 비교하여 변동 폭을 계산하는 함수"""
    try:
        res = requests.get(current_url, headers=HEADERS)
        if res.status_code != 200:
            return "미진입🚨"
            
        soup = BeautifulSoup(res.text, "html.parser")
        
        # 1. 한국 시간 기준으로 현재 시각과 1시간 전 시각 구하기
        kst_now = get_kst_now()
        kst_prev = kst_now - timedelta(hours=1)
        
        today_str = kst_now.strftime("%Y%m%d")
        prev_date_str = kst_prev.strftime("%Y%m%d")
        
        current_hour = kst_now.hour
        prev_hour = kst_prev.hour
        
        # 2. 가이섬 행(tr) 파싱
        all_rows = soup.find_all("tr")
        
        curr_element = None
        prev_element = None
        
        # 오늘 행과 (필요시) 어제 행에서 각각 해당 시간 칸 찾기
        for row in all_rows:
            first_cell = row.find("td")
            if first_cell:
                if today_str in first_cell.text:
                    curr_element = row.find("td", class_=f"thour{current_hour}")
                if prev_date_str in first_cell.text:
                    prev_element = row.find("td", class_=f"thour{prev_hour}")
        
        # 3. 변동 판독 로직
        is_curr_out = check_chart_out(curr_element)
        is_prev_out = check_chart_out(prev_element)
        
        if is_curr_out:
            return "미진입🚨"
            
        curr_rank = int(curr_element.text.strip())
        
        if is_prev_out:
            return f"{curr_rank}위( - )"
            
        prev_rank = int(prev_element.text.strip())
        
        # 순위 비교 (순위 숫자가 낮아질수록 오른 것임)
        if curr_rank < prev_rank:
            return f"{curr_rank}위( ▲ {prev_rank - curr_rank} )"
        elif curr_rank > prev_rank:
            return f"{curr_rank}위( ▼ {curr_rank - prev_rank} )"
        else:
            return f"{curr_rank}위( - )"
            
    except:
        return "미진입🚨"

def main():
    kst_now = get_kst_now()
    current_time_str = kst_now.strftime("%m/%d %H시")
    
    # 순위 및 변동폭 계산
    m_rt = calculate_change(f"https://xn--o39an51b2re.com/chart/melon/realtime/trend/ranking/{TRACK_IDS['melon_realtime']}") if TRACK_IDS['melon_realtime'] else "미진입🚨"
    m_top = calculate_change(f"https://xn--o39an51b2re.com/chart/melon/top100/trend/ranking/{TRACK_IDS['melon_top100']}") if TRACK_IDS['melon_top100'] else "미진입🚨"
    m_hot = calculate_change(f"https://xn--o39an51b2re.com/chart/melon/hot100-d30/trend/ranking/{TRACK_IDS['melon_hot100']}") if TRACK_IDS['melon_hot100'] else "미진입🚨"
    flo = calculate_change(f"https://xn--o39an51b2re.com/chart/flo/24hour/trend/ranking/{TRACK_IDS['flo_chart']}") if TRACK_IDS['flo_chart'] else "미진입🚨"
    genie = calculate_change(f"https://xn--o39an51b2re.com/chart/genie/realtime/trend/ranking/{TRACK_IDS['genie_realtime']}") if TRACK_IDS['genie_realtime'] else "미진입🚨"
    bugs = calculate_change(f"https://xn--o39an51b2re.com/chart/bugs/realtime/trend/ranking/{TRACK_IDS['bugs_realtime']}") if TRACK_IDS['bugs_realtime'] else "미진입🚨"

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
