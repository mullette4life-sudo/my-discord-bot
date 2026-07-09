import requests
from bs4 import BeautifulSoup
from datetime import datetime

# ==========================================
# [설정 부분] 나중에 곡이 발매되면 여기만 수정하세요!
# ==========================================
TARGET_TRACK_NAME = "연준 - Talk to You"
MELON_TRACK_ID = "600451251"  # 가이섬 멜론 주소 뒷부분 숫자 (현재 예시값)

# 디스코드 웹훅 URL (디스코드 채널 설정 -> 연동 -> 웹훅 만들기에서 생성된 URL)
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1524901754674872564/TXclUDd3qlaRFtMQoqCtCQhMOteXphf9_3wPi4DAKa0K13GjsKeomVBqNf92YL9touW0"
# ==========================================

def get_melon_rank():
    url = f"https://xn--o39an51b2re.com/chart/melon/realtime/trend/ranking/{MELON_TRACK_ID}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            return "사이트 접속 불가"
            
        soup = BeautifulSoup(res.text, "html.parser")
        
        # 현재 시각(0~23시)을 기준으로 해당 시간의 태그를 찾습니다.
        # 예: 현재가 오후 4시(16시)라면 클래스가 'thour16'인 태그를 찾음
        current_hour = datetime.now().hour
        target_class = f"thour{current_hour}"
        
        rank_element = soup.find("td", class_=target_class)
        
        if rank_element:
            rank_text = rank_element.text.strip()
            # 숫자가 비어있거나 배경색이 black인 경우 차트아웃 처리
            if not rank_text or "background-color: black" in str(rank_element):
                return "❌ 차트아웃"
            return f"🔥 {rank_text}위"
        else:
            return "❌ 차트아웃 (데이터 없음)"
            
    except Exception as e:
        return f"오류 발생 ({str(e)})"

def main():
    current_time_str = datetime.now().strftime("%Y-%m-%d %H:00")
    melon_rank = get_melon_rank()
    
    # 디스코드에 보낼 메시지 형태
    message_content = (
        f"📊 **{TARGET_TRACK_NAME} 실시간 차트 알림** ({current_time_str})\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🟢 **Melon 실시간:** {melon_rank}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
    )
    
    payload = {"content": message_content}
    requests.post(DISCORD_WEBHOOK_URL, json=payload)

if __name__ == "__main__":
    main()
