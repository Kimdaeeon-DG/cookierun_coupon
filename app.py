import streamlit as st
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
import time
import ssl

# SSL 인증서 에러 방지
ssl._create_default_https_context = ssl._create_unverified_context

st.set_page_config(page_title="쿠키런 자동 등록기", page_icon="🍪")
st.title("🍪 카카오 쿠키런 완벽 등록기")

kakao_id = st.text_input("카카오 회원번호(kakaoId)", placeholder="숫자만 입력")


def create_driver():
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--lang=ko-KR")
    return uc.Chrome(options=options)


def wait_for_coupon_inputs(driver, wait):
    """
    쿠폰 입력칸만 최대한 정확하게 찾기
    1차: maxlength=4 인 input
    2차: 화면에 보이는 input 중 앞의 4개
    """
    try:
        inputs = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input[maxlength='4']"))
        )
        visible_inputs = [inp for inp in inputs if inp.is_displayed() and inp.is_enabled()]
        if len(visible_inputs) >= 4:
            return visible_inputs[:4]
    except:
        pass

    all_inputs = wait.until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "input"))
    )
    visible_inputs = [inp for inp in all_inputs if inp.is_displayed() and inp.is_enabled()]
    if len(visible_inputs) >= 4:
        return visible_inputs[:4]

    raise Exception("쿠폰 입력칸 4개를 찾지 못했습니다.")


def safe_fill_input(input_el, value):
    """
    분할 입력칸에 값 안정적으로 입력
    """
    input_el.click()
    time.sleep(0.1)

    input_el.send_keys(Keys.CONTROL, "a")
    input_el.send_keys(Keys.DELETE)
    time.sleep(0.1)

    input_el.send_keys(value)
    time.sleep(0.2)

    actual = input_el.get_attribute("value")
    return actual


def collect_alert_messages(driver, max_wait_per_alert=3, max_alerts=5):
    """
    뜨는 alert를 최대한 다 수집
    """
    messages = []

    for _ in range(max_alerts):
        try:
            WebDriverWait(driver, max_wait_per_alert).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            msg = alert.text.strip()
            messages.append(msg)
            alert.accept()
            time.sleep(0.4)
        except TimeoutException:
            break
        except Exception as e:
            messages.append(f"팝업 처리 중 예외 발생: {e}")
            break

    return messages


def submit_one_coupon(kakao_id, coupon):
    driver = None
    result = {
        "coupon": coupon,
        "success": False,
        "messages": [],
        "error": None
    }

    try:
        driver = create_driver()
        wait = WebDriverWait(driver, 15)

        url = (
            f"https://cookierun.devscake.com/coupon.html"
            f"?kakaoId={kakao_id}&osType=I&_t={int(time.time() * 1000)}"
        )
        driver.get(url)
        time.sleep(2)

        inputs = wait_for_coupon_inputs(driver, wait)

        parts = [coupon[i:i+4] for i in range(0, len(coupon), 4)]

        if len(parts) != 4:
            raise Exception(f"쿠폰 길이가 16자가 아닙니다: {coupon}")

        # 4칸 입력 및 검증
        for idx, part in enumerate(parts):
            actual = safe_fill_input(inputs[idx], part)

            if actual != part:
                # 한 번 더 재시도
                actual = safe_fill_input(inputs[idx], part)
                if actual != part:
                    raise Exception(
                        f"{idx + 1}번째 입력칸 입력 실패 - 기대값: {part}, 실제값: {actual}"
                    )

        # 버튼 찾기
        submit_btn = wait.until(
            EC.element_to_be_clickable((By.ID, "submit-general"))
        )

        driver.execute_script("arguments[0].click();", submit_btn)
        time.sleep(0.5)

        messages = collect_alert_messages(driver)
        result["messages"] = messages if messages else ["서버 응답 팝업이 없습니다."]

        # 성공/실패 판별
        joined = " ".join(result["messages"])
        if ("완료" in joined) or ("등록" in joined) or ("성공" in joined) or ("이미 사용" in joined):
            result["success"] = True
        else:
            result["success"] = False

    except Exception as e:
        result["error"] = str(e)

    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

    return result


if st.button("🚀 3종 쿠폰 일괄 등록"):
    if not kakao_id:
        st.error("회원번호를 입력해주세요!")
    elif not kakao_id.isdigit():
        st.error("회원번호는 숫자만 입력해주세요!")
    else:
        coupons = [
            "AMAZINGKIWICOOK2",
            "ALWAYSS2BIKEKIWI",
            "DEVNOW2026THANKU"
        ]

        with st.status("🛠️ 쿠폰 등록 시작...", expanded=True) as status:
            success_count = 0

            for idx, coupon in enumerate(coupons, start=1):
                st.write(f"⚙️ [{idx}/{len(coupons)}] {coupon} 처리 중...")

                result = submit_one_coupon(kakao_id, coupon)

                if result["error"]:
                    st.error(f"❌ {coupon} 처리 실패: {result['error']}")
                    continue

                for msg in result["messages"]:
                    st.info(f"💬 {coupon} → {msg}")

                if result["success"]:
                    success_count += 1
                    st.success(f"✅ {coupon} 처리 완료")
                else:
                    st.warning(f"⚠️ {coupon} 처리 결과를 확인해주세요")

                time.sleep(1)

            status.update(
                label=f"✅ 작업 완료! ({success_count}/{len(coupons)}개 처리)",
                state="complete",
                expanded=False
            )

            st.balloons()
