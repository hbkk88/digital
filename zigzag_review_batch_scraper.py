import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def scrape_single_zigzag_review(url, file_index):
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    time.sleep(3)  # 페이지 초기 로딩 대기

    # 스크롤
    last_height = driver.execute_script("return document.body.scrollHeight")
    for i in range(30):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        print(f"[{file_index}] 스크롤 {i+1}회 완료")

    # 렌더링 대기 (중요!)
    time.sleep(2)

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[class^='css-vbvoj0']"))
        )
    except Exception as e:
        print(f"[{file_index}] 리뷰 요소 로딩 실패 → 건너뜀: {e}")
        driver.quit()
        return

    reviews = []
    review_elements = driver.find_elements(By.CSS_SELECTOR, "div[class^='css-vbvoj0']")
    print(f"[{file_index}] 리뷰 요소 {len(review_elements)}개 발견")

    for el in review_elements:
        try:
            content = el.text.strip()
            if content:
                reviews.append({"review": content})
        except:
            continue

    driver.quit()

    df = pd.DataFrame(reviews)
    output_path = rf"C:\Users\김해빈\Desktop\기말프로젝트\zigzag_reviews_{file_index}.csv"
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"[{file_index}] 저장 완료 → {output_path}")

def batch_scrape_zigzag_reviews(url_list):
    for idx, url in enumerate(url_list, start=1):
        try:
            print(f"\n=== [{idx}] {url} 시작 ===")
            scrape_single_zigzag_review(url, file_index=idx)
        except Exception as e:
            print(f"[{idx}] ⚠️ URL 처리 실패 → 건너뜀: {e}")

if __name__ == "__main__":
    url_list = [
        "https://zigzag.kr/review/list/122550593",
        "https://zigzag.kr/review/list/162362707",
        "https://zigzag.kr/review/list/129076367",
	"https://zigzag.kr/review/list/158971418",
	"https://zigzag.kr/review/list/141913686",
	"https://zigzag.kr/review/list/141373178",
	"https://zigzag.kr/review/list/140796259",
	"https://zigzag.kr/review/list/135005605",
	"https://zigzag.kr/review/list/135006673",
	"https://zigzag.kr/review/list/129150099",
	"https://zigzag.kr/review/list/141360643",
	"https://zigzag.kr/review/list/158203927"
    ]
    batch_scrape_zigzag_reviews(url_list)
