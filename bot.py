import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone

# =========================================================================
# [설정 부분] 나중에 곡이 발매되면 각 사이트의 가이섬 주소 맨 뒤 숫자(ID)를 적어주세요!
# =========================================================================
# 해시태그나 곡 제목 스타일로 자유롭게 수정 가능합니다.
TRACK_TAGS = "Ice Cream #IceCream 실시간 순위"

TRACK_IDS = {
    "melon_realtime": "602450078", # 멜론 실시간 트렌드 ID (현재 예시값)
    "melon_top100":   "602450078",          # 멜론 Top 100 ID
    "melon_hot100":   "602450078",          # 멜론 Hot 100 ID
    "flo_chart":      "595700972",          # 플로 차트 ID
    "genie_realtime": "115753952",          # 지니 실시간 ID
    "bugs_realtime":  "6488138"           # 벅스 실시간 ID
}

# 디스코드 웹훅 URL을 여기에 꼭 넣어주세요!
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1524901754674872564/TXclUDd3qlaRFtMQoqCtCQhMOteXphf9_3wPi4DAKa0K13GjsKeomVBqNf92YL9touW0"
# =========================================================================

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_kst_now():
    """서버 위치와 상관없이 무조건 한국 시간(KST)을 반환하는 함수"""
    # UTC+9인 한국 시간대 설정
    kst_zone = timezone(timedelta(hours=9))
    return datetime.now(kst_zone)
    
def parse_guyso_rank(url):
    """가이섬 사이트에서 '오늘 날짜'의 '현재 시간' 순위를 정확히 긁어오는 함수"""
    try:
        res = requests.get(url, headers=HEADERS)
        if res.status_code != 200:
            return "미진입🚨"
            
        soup = BeautifulSoup(res.text, "html.parser")
        
        # 1. 오늘 날짜 문자열 만들기 (예: "20260710")
        today_str = datetime.now().strftime("%Y%m%d")
        
        # 2. 현재 시간 구하기 (예: 8)
        current_hour = datetime.now().hour
        target_class = f"thour{current_hour}"
        
        # 3. 가이섬 표의 모든 행(tr)을 하나씩 검사합니다.
        all_rows = soup.find_all("tr")
        target_row = None
        
        for row in all_rows:
            # 행의 첫 번째 칸(td)에 적힌 글자가 오늘 날짜와 일치하는지 확인
            first_cell = row.find("td")
            if first_cell and today_str in first_cell.text:
                target_row = row  # 오늘 날짜 행을 찾음!
                break
        
        # 4. 오늘 날짜 행을 찾았다면, 그 행 안에서 현재 시간 칸을 찾습니다.
        if target_row:
            rank_element = target_row.find("td", class_=target_class)
            if rank_element:
                rank_text = rank_element.text.strip()
                # 숫자가 없거나 배경색이 검은색(차트아웃)인 경우 처리
                if not rank_text or "background-color: black" in str(rank_element) or "background: black" in str(rank_element):
                    return "미진입🚨"
                return f"{rank_text}위"
        
        # 오늘 날짜 행이 없거나(아직 오늘 데이터가 안 올라옴), 시간 칸이 없으면 미진입 처리
        return "미진입🚨"
    except:
        return "미진입🚨"
        
def main():
    # 05/31 20시 형태로 시간 포맷팅
    current_time_str = datetime.now().strftime("%m/%d %H시")
    
    # 각 차트별 크롤링 (ID가 없으면 미진입 처리)
    m_rt = parse_guyso_rank(f"https://xn--o39an51b2re.com/chart/melon/realtime/trend/ranking/{TRACK_IDS['melon_realtime']}") if TRACK_IDS['melon_realtime'] else "미진입🚨"
    m_top = parse_guyso_rank(f"https://xn--o39an51b2re.com/chart/melon/top100/trend/ranking/{TRACK_IDS['melon_top100']}") if TRACK_IDS['melon_top100'] else "미진입🚨"
    m_hot = parse_guyso_rank(f"https://xn--o39an51b2re.com/chart/melon/hot100-d30/trend/ranking/{TRACK_IDS['melon_hot100']}") if TRACK_IDS['melon_hot100'] else "미진입🚨"
    flo = parse_guyso_rank(f"https://xn--o39an51b2re.com/chart/flo/24hour/trend/ranking/{TRACK_IDS['flo_chart']}") if TRACK_IDS['flo_chart'] else "미진입🚨"
    genie = parse_guyso_rank(f"https://xn--o39an51b2re.com/chart/genie/realtime/trend/ranking/{TRACK_IDS['genie_realtime']}") if TRACK_IDS['genie_realtime'] else "미진입🚨"
    bugs = parse_guyso_rank(f"https://xn--o39an51b2re.com/chart/bugs/realtime/trend/ranking/{TRACK_IDS['bugs_realtime']}") if TRACK_IDS['bugs_realtime'] else "미진입🚨"

    # 💡 요청하신 이미지와 똑같은 형태로 메시지 조립
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
    
    # 디스코드 전송
    payload = {"content": message_content}
    requests.post(DISCORD_WEBHOOK_URL, json=payload)

if __name__ == "__main__":
    main()
