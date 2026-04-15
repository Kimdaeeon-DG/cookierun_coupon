import streamlit as st
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

st.set_page_config(page_title="쿠키런 정밀 등록기", page_icon="🍪")
st.title("🍪 카카오 쿠키런 정밀 등록기")

kakao_id = st.text_input("카카오 회원번호(kakaoId)", placeholder="숫자만 입력")

if st.button("🚀 3종 쿠폰 정밀 등록 시작"):
    if not kakao_id:
        st.error("회원번호를 입력해주세요!")
    else:
        with st.status("🛠️ 정밀 입력 모드 가동 중...", expanded=True) as status:
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
                    st.write(f"⚙️ [{i+1}/3] {coupon} 입력 시도...")
                    
                    # 1. 확실한 페이지 초기화
                    driver.get(url)
                    time.sleep(2) # 모바일 대응을 위한 충분한 로딩 시간
                    
                    try:
                        # 2. 입력창 요소 확보
                        inputs = wait.until(EC.visibility_of_all_elements_located((By.TAG_NAME, "input")))
                        parts = [coupon[j:j+4] for j in range(0, len(coupon), 4)]
                        
                        # 3. [보완] 각 칸을 클릭한 후 입력 (입력 씹힘 방지)
                        for idx, part in enumerate(parts):
                            if idx < len(inputs):
                                # 자바스크립트로 칸을 비우고, 클릭해서 포커스를 준 뒤 타이핑
                                driver.execute_script("arguments[0].value = '';", inputs[idx])
                                inputs[idx].click() 
                                inputs[idx].send_keys(part)
                                time.sleep(0.2) # 입력 사이의 아주 짧은 간격
                        
                        # 4. 버튼 클릭
                        btn = wait.until(EC.element_to_be_clickable((By.ID, "submit-general")))
                        driver.execute_script("arguments[0].click();", btn)
                        
                        # 5. 모든 팝업 처리
                        while True:
                            try:
                                WebDriverWait(driver, 5).until(EC.alert_is_present())
                                alert = driver.switch_to.alert
                                msg = alert.text
                                alert.accept()
                                st.info(f"💬 결과: {msg}")
                                time.sleep(1)
                            except:
                                break
                                
                    except Exception as e:
                        st.warning(f"⚠️ {coupon}: 입력 중 튕김 현상 발생 (다음으로 이동)")
                        continue
                    
                    time.sleep(1.5) # 쿠폰 간 안전 간격

                status.update(label="✅ 모든 쿠폰 등록 완료!", state="complete", expanded=False)
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ 치명적 오류: {e}")
            finally:
                if 'driver' in locals():
                    driver.quit()
