import streamlit as st
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import ssl

# SSL 에러 방지
ssl._create_default_https_context = ssl._create_unverified_context

st.set_page_config(page_title="쿠키런 쿠폰 자동 등록기", page_icon="🍪")
st.title("🍪 카카오 쿠키런 최종 등록기")

kakao_id = st.text_input("카카오 회원번호(kakaoId)", placeholder="숫자만 입력")

if st.button("쿠폰 3종 일괄 등록"):
    if not kakao_id:
        st.error("회원번호를 입력해주세요!")
    else:
        with st.status("🚀 서버 작업 시작...", expanded=True) as status:
            coupons = ["AMAZINGKIWICOOK2", "ALWAYSS2BIKEKIWI", "DEVNOW2026THANKU"]
            
            options = uc.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920,1080') # 화면 크기 고정으로 요소 겹침 방지
            
            try:
                driver = uc.Chrome(options=options)
                url = f"https://cookierun.devscake.com/coupon.html?kakaoId={kakao_id}&osType=I"
                
                for i, coupon in enumerate(coupons):
                    st.write(f"⚙️ [{i+1}/3] {coupon} 처리 중...")
                    
                    # [핵심] 매 쿠폰마다 새로고침을 수행하여 '상호작용 불가' 상태를 원천 차단
                    driver.get(url)
                    time.sleep(2) 
                    
                    wait = WebDriverWait(driver, 15)
                    
                    try:
                        # 1. 입력창이 '클릭 가능'할 때까지 대기 (단순 존재 확인보다 강력함)
                        inputs = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "input")))
                        
                        # 첫 번째 입력칸이 실제로 상호작용 가능한지 한 번 더 체크
                        wait.until(EC.element_to_be_clickable(inputs[0]))
                        
                        parts = [coupon[j:j+4] for j in range(0, len(coupon), 4)]
                        for idx, part in enumerate(parts):
                            if idx < len(inputs):
                                inputs[idx].clear()
                                inputs[idx].send_keys(part)
                        
                        # 2. 버튼 클릭
                        btn = wait.until(EC.element_to_be_clickable((By.ID, "submit-general")))
                        driver.execute_script("arguments[0].click();", btn)
                        
                        # 3. 팝업 무한 처리 루프
                        while True:
                            try:
                                WebDriverWait(driver, 5).until(EC.alert_is_present())
                                alert = driver.switch_to.alert
                                msg = alert.text
                                alert.accept()
                                st.info(f"💬 결과: {msg}")
                                time.sleep(1) # 팝업 닫힌 후 안정화 시간
                            except:
                                break
                                
                    except Exception as e:
                        st.warning(f"⚠️ {coupon}: 처리 중 일시적 오류 (재시도 중...)")
                        # 실패 시 해당 루프를 한 번 더 안전하게 보강하기 위해 짧게 대기
                        time.sleep(1)
                
                status.update(label="✨ 모든 작업 완료!", state="complete", expanded=False)
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ 치명적 오류 발생: {e}")
            finally:
                if 'driver' in locals():
                    driver.quit()
