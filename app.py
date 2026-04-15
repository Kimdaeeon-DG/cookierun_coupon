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
st.title("🍪 쿠런 쿠폰 무한 루프 등록기")

kakao_id = st.text_input("카카오 회원번호(kakaoId)", placeholder="숫자만 입력")

if st.button("🚀 3종 쿠폰 확실하게 등록"):
    if not kakao_id:
        st.error("회원번호를 입력해주세요!")
    else:
        with st.status("🛠️ 엔진 가동 중...", expanded=True) as status:
            coupons = ["AMAZINGKIWICOOK2", "ALWAYSS2BIKEKIWI", "DEVNOW2026THANKU"]
            
            options = uc.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920,1080')
            
            try:
                driver = uc.Chrome(options=options)
                # 초기 접속
                base_url = f"https://cookierun.devscake.com/coupon.html?kakaoId={kakao_id}&osType=I"
                driver.get(base_url)
                
                for i, coupon in enumerate(coupons):
                    st.write(f"⚙️ [{i+1}/3] {coupon} 시도 중...")
                    
                    # 1. [핵심] 이전 작업의 흔적을 지우기 위해 강제 새로고침 후 대기
                    driver.refresh() 
                    time.sleep(3) # 모바일/서버 환경을 위해 충분히 대기 (입력창 재생성 시간)
                    
                    wait = WebDriverWait(driver, 15)
                    
                    try:
                        # 2. 입력창 4개 찾기
                        inputs = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "input")))
                        parts = [coupon[j:j+4] for j in range(0, len(coupon), 4)]
                        
                        # 3. 입력창이 다시 생겼으므로 깨끗한 상태에서 입력
                        for idx, part in enumerate(parts):
                            if idx < len(inputs):
                                target_input = inputs[idx]
                                target_input.click() # 칸 활성화
                                target_input.send_keys(part)
                        
                        # 4. 버튼 클릭
                        btn = wait.until(EC.element_to_be_clickable((By.ID, "submit-general")))
                        time.sleep(0.5) # 클릭 전 안정화
                        driver.execute_script("arguments[0].click();", btn)
                        
                        # 5. 팝업이 1~2개 생기는 것 모두 닫기
                        # 첫 번째 팝업 대기
                        wait.until(EC.alert_is_present())
                        
                        # 팝업이 더 이상 없을 때까지 반복
                        while True:
                            try:
                                alert = driver.switch_to.alert
                                msg = alert.text
                                alert.accept()
                                st.info(f"💬 결과: {msg}")
                                time.sleep(1) # 팝업 닫히는 애니메이션 시간 대기
                            except:
                                break # 팝업이 더 없으면 루프 탈출
                                
                    except Exception as e:
                        st.warning(f"⚠️ {coupon}: 입력창 로딩 지연으로 재시도합니다.")
                        continue
                    
                    # 한 사이클 종료 후 다음 쿠폰 전 여유 시간
                    time.sleep(1)

                status.update(label="✅ 모든 등록 절차 종료!", state="complete", expanded=False)
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ 치명적 오류: {e}")
            finally:
                if 'driver' in locals():
                    driver.quit()
