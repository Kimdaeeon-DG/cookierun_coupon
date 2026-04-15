import streamlit as st
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import ssl

# SSL 에러 방지
ssl._create_default_https_context = ssl._create_unverified_context

# 웹 화면 구성
st.set_page_config(page_title="쿠키런 쿠폰 자동 등록기", page_icon="🍪")
st.title("🍪 카카오 쿠키런 쿠폰 자동 등록")
st.write("회원번호를 입력하고 등록 버튼을 누르세요.")

kakao_id = st.text_input("카카오 회원번호(kakaoId)", placeholder="예: 123821116865")

if st.button("쿠폰 3종 자동 등록 시작"):
    if not kakao_id:
        st.error("회원번호를 입력해주세요!")
    else:
        with st.status("🚀 브라우저 구동 및 쿠폰 등록 중...", expanded=True) as status:
            coupons = ["amazingkiwicook2", "alwayss2bikekiwi", "DEVNOW2026THANKU"]
            
            # 서버용 크롬 설정
            options = uc.ChromeOptions()
            options.add_argument('--headless') # 서버에서는 반드시 창 없는 모드여야 함
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            driver = uc.Chrome(options=options)
            
            try:
                url = f"https://cookierun.devscake.com/coupon.html?kakaoId={kakao_id}&osType=I"
                
                for i, coupon in enumerate(coupons):
                    driver.get(url)
                    clean_coupon = coupon.replace(" ", "").upper()
                    st.write(f"⚙️ [{i+1}/3] {clean_coupon} 입력 중...")
                    
                    wait = WebDriverWait(driver, 10)
                    
                    # 입력 및 클릭 로직
                    inputs = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "input")))
                    parts = [clean_coupon[i:i+4] for i in range(0, len(clean_coupon), 4)]
                    for idx, part in enumerate(parts):
                        if idx < len(inputs):
                            inputs[idx].send_keys(part)
                    
                    btn = driver.find_element(By.ID, "submit-general")
                    driver.execute_script("arguments[0].click();", btn)
                    
                    # 팝업 처리
                    wait.until(EC.alert_is_present())
                    alert = driver.switch_to.alert
                    st.success(f"✅ {clean_coupon}: {alert.text}")
                    alert.accept()
                    time.sleep(1)
                
                status.update(label="✨ 모든 쿠폰 등록 완료!", state="complete", expanded=False)
                st.balloons() # 축하 효과
                
            except Exception as e:
                st.error(f"오류 발생: {e}")
            finally:
                driver.quit()
