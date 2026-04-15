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
            
            try:
                driver = uc.Chrome(options=options)
                url = f"https://cookierun.devscake.com/coupon.html?kakaoId={kakao_id}&osType=I"
                
                # 처음 한 번만 페이지 로드 (속도 향상)
                driver.get(url)
                
                for i, coupon in enumerate(coupons):
                    st.write(f"⚙️ [{i+1}/3] {coupon} 처리 중...")
                    wait = WebDriverWait(driver, 10)
                    
                    try:
                        # 1. 입력창 대기 및 입력
                        inputs = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "input")))
                        parts = [coupon[j:j+4] for j in range(0, len(coupon), 4)]
                        for idx, part in enumerate(parts):
                            if idx < len(inputs):
                                inputs[idx].clear()
                                inputs[idx].send_keys(part)
                        
                        # 2. 버튼 클릭
                        btn = driver.find_element(By.ID, "submit-general")
                        driver.execute_script("arguments[0].click();", btn)
                        
                        # 3. [핵심 수정] 모든 팝업이 사라질 때까지 반복 처리
                        # unexpected alert open 에러를 방지하기 위해 루프를 돕니다.
                        while True:
                            try:
                                WebDriverWait(driver, 4).until(EC.alert_is_present())
                                alert = driver.switch_to.alert
                                msg = alert.text
                                alert.accept()
                                st.info(f"💬 결과: {msg}")
                                time.sleep(0.5) # 다음 팝업이 뜨는지 확인용 간격
                            except:
                                # 더 이상 팝업이 없으면 탈출
                                break
                                
                    except Exception as e:
                        st.warning(f"⚠️ {coupon}: 처리 지연 또는 오류 (내용: {str(e)[:50]}...)")
                        # 에러 발생 시 페이지 다시 로드해서 상태 초기화
                        driver.get(url)
                        time.sleep(1)
                
                status.update(label="✨ 모든 작업 완료!", state="complete", expanded=False)
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ 치명적 오류 발생: {e}")
            finally:
                if 'driver' in locals():
                    driver.quit()
