import streamlit as st
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import ssl

# SSL 인증서 에러 방지
ssl._create_default_https_context = ssl._create_unverified_context

st.set_page_config(page_title="쿠키런 통합 등록기", page_icon="🍪")
st.title("🍪 쿠키런 전 기기 통합 등록기")

kakao_id = st.text_input("카카오 회원번호(kakaoId)", placeholder="숫자만 입력")

if st.button("🚀 3종 쿠폰 확실하게 등록"):
    if not kakao_id:
        st.error("회원번호를 입력해주세요!")
    else:
        with st.status("🛠️ 안정화 모드로 등록 시작...", expanded=True) as status:
            coupons = ["AMAZINGKIWICOOK2", "ALWAYSS2BIKEKIWI", "DEVNOW2026THANKU"]
            
            options = uc.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920,1080')
            
            try:
                driver = uc.Chrome(options=options)
                url = f"https://cookierun.devscake.com/coupon.html?kakaoId={kakao_id}&osType=I"
                wait = WebDriverWait(driver, 15)
                
                for i, coupon in enumerate(coupons):
                    st.write(f"⚙️ [{i+1}/3] {coupon} 시도 중...")
                    
                    # 1. 페이지 로드 후 '확실히' 기다리기
                    driver.get(url)
                    time.sleep(2) # 페이지가 완전히 로딩될 시간을 줌
                    
                    try:
                        # 2. 입력창 확보
                        inputs = wait.until(EC.visibility_of_all_elements_located((By.TAG_NAME, "input")))
                        parts = [coupon[j:j+4] for j in range(0, len(coupon), 4)]
                        
                        # 3. 데이터 입력 (각 칸마다 아주 미세한 간격)
                        for idx, part in enumerate(parts):
                            if idx < len(inputs):
                                inputs[idx].click()
                                inputs[idx].clear()
                                inputs[idx].send_keys(part)
                        
                        # 4. 버튼 클릭
                        btn = wait.until(EC.element_to_be_clickable((By.ID, "submit-general")))
                        time.sleep(0.5) # 클릭 전 잠시 대기
                        driver.execute_script("arguments[0].click();", btn)
                        
                        # 5. 모든 팝업 처리 (없어질 때까지 끈질기게)
                        count = 0
                        while count < 3: # 최대 3개 팝업까지 대응
                            try:
                                WebDriverWait(driver, 5).until(EC.alert_is_present())
                                alert = driver.switch_to.alert
                                msg = alert.text
                                alert.accept()
                                st.info(f"💬 결과: {msg}")
                                time.sleep(1) # 팝업 닫힌 후 브라우저 안정화 시간
                                count += 1
                            except:
                                break
                                
                    except Exception as e:
                        st.warning(f"⚠️ {coupon}: 등록 중 지연 발생 (다음 쿠폰으로 이동)")
                        continue
                    
                    # 다음 쿠폰으로 넘어가기 전 1초 휴식
                    time.sleep(1)

                status.update(label="✅ 모든 등록 절차 종료!", state="complete", expanded=False)
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ 오류: {e}")
            finally:
                if 'driver' in locals():
                    driver.quit()
