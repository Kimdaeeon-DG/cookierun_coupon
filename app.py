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
st.title("🍪 카카오 쿠키런 자동 등록기")

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
                url = f"https://cookierun.devscake.com/coupon.html?kakaoId={kakao_id}&osType=I"
                wait = WebDriverWait(driver, 15)
                
                for i, coupon in enumerate(coupons):
                    st.write(f"⚙️ [{i+1}/3] {coupon} 시도 중...")
                    
                    # [규칙 4] 매 쿠폰마다 무조건 주소로 새로 접속하여 깨끗한 상태 만들기
                    driver.get(url)
                    time.sleep(2) # 입력창이 완전히 만들어질 때까지 대기
                    
                    try:
                        # [규칙 1 & 2] 입력창을 찾고, 4글자씩 잘라서 넣기
                        inputs = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "input")))
                        parts = [coupon[j:j+4] for j in range(0, len(coupon), 4)]
                        
                        for idx, part in enumerate(parts):
                            if idx < len(inputs):
                                inputs[idx].send_keys(part)
                                time.sleep(0.1) # 타자 치는 속도 조절
                        
                        # 버튼 클릭 (누르는 순간 입력창은 사라짐)
                        btn = wait.until(EC.element_to_be_clickable((By.ID, "submit-general")))
                        driver.execute_script("arguments[0].click();", btn)
                        
                        # [규칙 3] 팝업 1~3개 처리 (가장 중요한 부분)
                        popups_handled = 0
                        while True:
                            try:
                                # 최대 3초 동안 팝업이 뜨는지 '매번' 기다려봅니다.
                                WebDriverWait(driver, 3).until(EC.alert_is_present())
                                alert = driver.switch_to.alert
                                msg = alert.text
                                alert.accept()
                                st.info(f"💬 서버 응답: {msg}")
                                popups_handled += 1
                                time.sleep(0.5) # 팝업 닫고 다음 팝업이 뜰 때까지의 미세한 간격 대기
                            except:
                                # 3초 동안 기다렸는데도 아무 팝업이 안 뜨면? -> 끝났다고 판단!
                                break
                                
                    except Exception as e:
                        st.warning(f"⚠️ {coupon} 처리 중 에러 발생, 다음으로 넘어갑니다.")
                        continue
                    
                    # 한 쿠폰이 완전히 끝나면 다음 쿠폰으로 넘어가기 전 1초 휴식
                    time.sleep(1)

                status.update(label="✅ 모든 작업이 완료되었습니다!", state="complete", expanded=False)
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ 치명적 오류: {e}")
            finally:
                if 'driver' in locals():
                    driver.quit()
