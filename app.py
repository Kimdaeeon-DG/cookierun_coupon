import streamlit as st
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import ssl

# SSL 인증서 에러 방지
ssl._create_default_https_context = ssl._create_unverified_context

st.set_page_config(page_title="쿠키런 쿠폰 자동 등록기", page_icon="🍪")
st.title("🍪 카카오 쿠키런 쿠폰 자동 등록")
st.info("이미 등록된 쿠폰은 자동으로 확인하고 다음 단계로 넘어갑니다.")

kakao_id = st.text_input("카카오 회원번호(kakaoId)", placeholder="예: 123821116865")

if st.button("쿠폰 3종 자동 등록 시작"):
    if not kakao_id:
        st.error("회원번호를 입력해주세요!")
    else:
        with st.status("🚀 서버 가동 중...", expanded=True) as status:
            coupons = ["amazingkiwicook2", "alwayss2bikekiwi", "DEVNOW2026THANKU"]
            
            options = uc.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            
            try:
                driver = uc.Chrome(options=options)
                url = f"https://cookierun.devscake.com/coupon.html?kakaoId={kakao_id}&osType=I"
                
                for i, coupon in enumerate(coupons):
                    clean_coupon = coupon.replace(" ", "").upper()
                    st.write(f"🔍 [{i+1}/3] {clean_coupon} 확인 중...")
                    
                    # 매번 새로고침하여 입력창 상태 초기화
                    driver.get(url)
                    time.sleep(1.5) 
                    
                    wait = WebDriverWait(driver, 10)
                    
                    # 1. 입력창에 4글자씩 입력
                    try:
                        inputs = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "input")))
                        parts = [clean_coupon[i:i+4] for i in range(0, len(clean_coupon), 4)]
                        for idx, part in enumerate(parts):
                            if idx < len(inputs):
                                inputs[idx].clear()
                                inputs[idx].send_keys(part)
                        
                        # 2. 이미지 버튼 클릭
                        btn = wait.until(EC.element_to_be_clickable((By.ID, "submit-general")))
                        driver.execute_script("arguments[0].click();", btn)
                        
                        # 3. 알림창 처리 (성공이든 중복이든 상관없이 닫기)
                        WebDriverWait(driver, 8).until(EC.alert_is_present())
                        alert = driver.switch_to.alert
                        msg = alert.text
                        alert.accept()
                        
                        if "성공" in msg or "지급" in msg:
                            st.success(f"✨ {clean_coupon}: 성공! ({msg})")
                        elif "이미" in msg or "사용" in msg:
                            st.warning(f"⏭️ {clean_coupon}: 이미 등록됨 (건너뜀)")
                        else:
                            st.info(f"💡 {clean_coupon}: {msg}")
                            
                    except Exception as e:
                        st.error(f"⚠️ {clean_coupon} 처리 중 건너뜀 (사유: {e})")
                        continue # 에러 나도 다음 쿠폰으로 이동
                        
                    time.sleep(1) # 서버 과부하 방지
                
                status.update(label="✨ 모든 쿠폰 확인 완료!", state="complete", expanded=False)
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ 치명적 오류: {e}")
            finally:
                if 'driver' in locals():
                    driver.quit()
