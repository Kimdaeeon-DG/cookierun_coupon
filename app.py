import streamlit as st
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import ssl

# SSL 인증서 에러 방지
ssl._create_default_https_context = ssl._create_unverified_context

st.set_page_config(page_title="쿠키런 모바일 대응 등록기", page_icon="📱")
st.title("📱 카카오 쿠키런 전종 등록기")

kakao_id = st.text_input("카카오 회원번호(kakaoId)", placeholder="숫자만 입력")

if st.button("🚀 무조건 일괄 등록"):
    if not kakao_id:
        st.error("회원번호를 입력해주세요!")
    else:
        with st.status("🛠️ 모바일 최적화 엔진 구동 중...", expanded=True) as status:
            coupons = ["AMAZINGKIWICOOK2", "ALWAYSS2BIKEKIWI", "DEVNOW2026THANKU"]
            
            options = uc.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920,1080')
            # 봇 감지 우회 추가 옵션
            options.add_argument("--disable-blink-features=AutomationControlled")
            
            try:
                driver = uc.Chrome(options=options)
                wait = WebDriverWait(driver, 10)
                url = f"https://cookierun.devscake.com/coupon.html?kakaoId={kakao_id}&osType=I"
                
                for i, coupon in enumerate(coupons):
                    st.write(f"🔄 [{i+1}/3] {coupon} 시도 중...")
                    
                    # [수정] 매번 URL을 새로 호출하여 이전 쿠폰의 잔상을 완전히 제거
                    driver.get(url)
                    time.sleep(1.5) # 페이지가 안정화될 시간을 조금 줍니다.
                    
                    try:
                        # 1. 입력창 대기
                        inputs = wait.until(EC.visibility_of_all_elements_located((By.TAG_NAME, "input")))
                        
                        # 2. 4글자씩 입력
                        parts = [coupon[j:j+4] for j in range(0, len(coupon), 4)]
                        for idx, part in enumerate(parts):
                            if idx < len(inputs):
                                inputs[idx].send_keys(part)
                        
                        # 3. 버튼 클릭
                        btn = wait.until(EC.element_to_be_clickable((By.ID, "submit-general")))
                        driver.execute_script("arguments[0].click();", btn)
                        
                        # 4. [핵심] 팝업 처리 - 팝업이 없어질 때까지 계속 닫기
                        # 모바일 에러 방지를 위해 타임아웃을 짧게 여러번 체크합니다.
                        for _ in range(3): # 최대 3개까지 연속 팝업 대응
                            try:
                                WebDriverWait(driver, 5).until(EC.alert_is_present())
                                alert = driver.switch_to.alert
                                msg = alert.text
                                alert.accept()
                                st.info(f"💬 {coupon} 결과: {msg}")
                                time.sleep(0.5)
                            except:
                                break # 더 이상 팝업 없으면 다음 쿠폰으로
                        
                    except Exception as e:
                        st.warning(f"⚠️ {coupon} 단계에서 지연이 발생하여 재접속합니다.")
                        continue # 다음 쿠폰으로 강제 진행

                status.update(label="✅ 모든 쿠폰 등록 시도 완료!", state="complete", expanded=False)
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ 치명적 오류: {e}")
            finally:
                if 'driver' in locals():
                    driver.quit()
