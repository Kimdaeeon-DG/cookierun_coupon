import streamlit as st
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import ssl

# SSL 인증서 에러 방지
ssl._create_default_https_context = ssl._create_unverified_context

st.set_page_config(page_title="쿠키런 초고속 등록기", page_icon="⚡")
st.title("⚡ 카카오 쿠키런 초고속 등록기")

kakao_id = st.text_input("카카오 회원번호(kakaoId)", placeholder="숫자만 입력")

if st.button("🚀 초고속 일괄 등록"):
    if not kakao_id:
        st.error("회원번호를 입력해주세요!")
    else:
        with st.status("⚡ 엔진 가동 중...", expanded=True) as status:
            coupons = ["AMAZINGKIWICOOK2", "ALWAYSS2BIKEKIWI", "DEVNOW2026THANKU"]
            
            options = uc.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920,1080')
            
            try:
                driver = uc.Chrome(options=options)
                url = f"https://cookierun.devscake.com/coupon.html?kakaoId={kakao_id}&osType=I"
                
                # 1. 처음 한 번만 페이지 로드
                driver.get(url)
                wait = WebDriverWait(driver, 5) # 대기 시간을 5초로 단축 (빠른 반응)
                
                for i, coupon in enumerate(coupons):
                    st.write(f"⚡ [{i+1}/3] {coupon} 처리 중...")
                    
                    try:
                        # [최적화] 자바스크립트로 모든 입력창의 찌꺼기 제거 (새로고침보다 훨씬 빠름)
                        driver.execute_script("document.querySelectorAll('input').forEach(i => i.value = '');")
                        
                        # 1. 입력창이 나타나자마자 낚아채기
                        inputs = wait.until(EC.visibility_of_all_elements_located((By.TAG_NAME, "input")))
                        
                        parts = [coupon[j:j+4] for j in range(0, len(coupon), 4)]
                        for idx, part in enumerate(parts):
                            if idx < len(inputs):
                                inputs[idx].send_keys(part)
                        
                        # 2. 버튼 클릭 (요소가 클릭 가능해지면 즉시 실행)
                        btn = wait.until(EC.element_to_be_clickable((By.ID, "submit-general")))
                        driver.execute_script("arguments[0].click();", btn)
                        
                        # 3. 팝업 즉시 처리 (등장하는 순간 낚아챔)
                        wait.until(EC.alert_is_present())
                        alert = driver.switch_to.alert
                        msg = alert.text
                        alert.accept()
                        
                        st.info(f"💬 결과: {msg}")
                        
                        # [핵심] 팝업을 닫은 후 페이지가 "클릭 가능한 상태"로 돌아올 때까지 '지능적' 대기
                        # 무작정 기다리는 게 아니라 브라우저가 준비되면 바로 넘어감
                        wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "modal-backdrop"))) # 잔상 제거 확인
                        
                    except Exception as e:
                        st.warning(f"⚠️ {coupon}: 빠른 재시도 중...")
                        driver.get(url) # 오류 시에만 새로고침

                status.update(label="✨ 등록 완료!", state="complete", expanded=False)
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ 오류: {e}")
            finally:
                if 'driver' in locals():
                    driver.quit()
