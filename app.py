import streamlit as st
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import ssl

# SSL 인증서 에러 방지
ssl._create_default_https_context = ssl._create_unverified_context

st.set_page_config(page_title="쿠키런 고속 등록기", page_icon="⚡")
st.title("⚡ 카카오 쿠키런 고속 등록기")

kakao_id = st.text_input("카카오 회원번호(kakaoId)", placeholder="숫자만 입력")

if st.button("🚀 일괄 등록 시작"):
    if not kakao_id:
        st.error("회원번호를 입력해주세요!")
    else:
        with st.status("⚡ 쿠폰 엔진 가동 중...", expanded=True) as status:
            coupons = ["AMAZINGKIWICOOK2", "ALWAYSS2BIKEKIWI", "DEVNOW2026THANKU"]
            
            options = uc.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920,1080')
            
            try:
                driver = uc.Chrome(options=options)
                url = f"https://cookierun.devscake.com/coupon.html?kakaoId={kakao_id}&osType=I"
                wait = WebDriverWait(driver, 10)
                
                for i, coupon in enumerate(coupons):
                    st.write(f"⚡ [{i+1}/3] {coupon} 시도 중...")
                    
                    # 1. 페이지 로드
                    driver.get(url)
                    
                    try:
                        # 2. 입력창 대기 및 입력
                        inputs = wait.until(EC.visibility_of_all_elements_located((By.TAG_NAME, "input")))
                        parts = [coupon[j:j+4] for j in range(0, len(coupon), 4)]
                        for idx, part in enumerate(parts):
                            if idx < len(inputs):
                                inputs[idx].send_keys(part)
                        
                        # 3. 버튼 클릭
                        btn = wait.until(EC.element_to_be_clickable((By.ID, "submit-general")))
                        driver.execute_script("arguments[0].click();", btn)
                        
                        # 4. [핵심] 팝업이 몇 개든 다 닫기
                        # 첫 번째 팝업은 무조건 기다리고, 그 다음부터는 즉시 확인해서 닫음
                        wait.until(EC.alert_is_present()) 
                        
                        while True:
                            try:
                                alert = driver.switch_to.alert
                                msg = alert.text
                                alert.accept()
                                st.info(f"💬 결과: {msg}")
                                time.sleep(0.5) # 팝업 사이의 짧은 간격
                            except:
                                # 더 이상 팝업이 없으면 탈출
                                break
                        
                    except Exception as e:
                        st.warning(f"⚠️ {coupon}: 등록 중 지연 발생")
                        continue

                status.update(label="✨ 등록 절차 완료!", state="complete", expanded=False)
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ 오류: {e}")
            finally:
                if 'driver' in locals():
                    driver.quit()
