import streamlit as st
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import ssl

# SSL 인증서 에러 방지
ssl._create_default_https_context = ssl._create_unverified_context

st.set_page_config(page_title="쿠키런 자동 등록기", page_icon="🍪")
st.title("🍪 카카오 쿠키런 완벽 등록기")

kakao_id = st.text_input("카카오 회원번호(kakaoId)", placeholder="숫자만 입력")

if st.button("🚀 3종 쿠폰 일괄 등록"):
    if not kakao_id:
        st.error("회원번호를 입력해주세요!")
    else:
        with st.status("🛠️ 쿠폰 등록 시작...", expanded=True) as status:
            coupons = ["AMAZINGKIWICOOK2", "ALWAYSS2BIKEKIWI", "DEVNOW2026THANKU"]
            
            options = uc.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920,1080')
            
            try:
                driver = uc.Chrome(options=options)
                base_url = f"https://cookierun.devscake.com/coupon.html?kakaoId={kakao_id}&osType=I"
                wait = WebDriverWait(driver, 15)
                
                for i, coupon in enumerate(coupons):
                    st.write(f"⚙️ [{i+1}/3] {coupon} 시도 중...")
                    
                    # [핵심 1] 주소 끝에 현재 시간을 붙여서 매번 '완전히 새로운 페이지'로 인식시킴
                    # 이렇게 하면 브라우저가 로딩을 완전히 끝낼 때까지 코드가 얌전히 기다립니다.
                    refresh_url = f"{base_url}&_t={time.time()}"
                    driver.get(refresh_url)
                    time.sleep(2) # 안전하게 추가 로딩 대기
                    
                    try:
                        # 1. 입력창 찾기
                        all_inputs = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "input")))
                        
                        # [핵심 2] 혹시 모를 투명한 숨김 입력칸을 피해 '눈에 보이는 칸'에만 입력
                        visible_inputs = [inp for inp in all_inputs if inp.is_displayed()]
                        
                        parts = [coupon[j:j+4] for j in range(0, len(coupon), 4)]
                        
                        # 2. 4글자씩 입력 (규칙 1 & 2)
                        for idx, part in enumerate(parts):
                            if idx < len(visible_inputs):
                                visible_inputs[idx].clear() # 찌꺼기 확실히 제거
                                visible_inputs[idx].send_keys(part)
                                time.sleep(0.1) 
                        
                        # 3. 버튼 클릭
                        btn = wait.until(EC.element_to_be_clickable((By.ID, "submit-general")))
                        driver.execute_script("arguments[0].click();", btn)
                        
                        # 4. 팝업 1~3개 대응 (규칙 3)
                        while True:
                            try:
                                # 최대 3초 동안 팝업이 뜨는지 계속 기다려봄
                                WebDriverWait(driver, 3).until(EC.alert_is_present())
                                alert = driver.switch_to.alert
                                msg = alert.text
                                alert.accept()
                                st.info(f"💬 서버 응답: {msg}")
                                time.sleep(0.5) 
                            except:
                                # 3초가 지나도 팝업이 없으면 완전히 닫혔다고 판단
                                break
                                
                    except Exception as e:
                        st.warning(f"⚠️ {coupon} 처리 중 문제 발생 (건너뜀)")
                        continue
                    
                    time.sleep(1)

                status.update(label="✅ 모든 작업이 완료되었습니다!", state="complete", expanded=False)
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ 치명적 오류: {e}")
            finally:
                if 'driver' in locals():
                    driver.quit()
