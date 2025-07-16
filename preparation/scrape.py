from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json

# ヘッドレスモード設定
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1200")
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/114.0.0.0 Safari/537.36"
)

# ChromeDriver を自動管理
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    url = "https://www.facultysearch.admin.saga-u.ac.jp/index.php"
    driver.get(url)

    # 「理工学系」ボタンをクリック
    btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[@name='sosiki' and normalize-space(text())='理工学系']")
        )
    )
    driver.execute_script("arguments[0].click();", btn)

    # 結果テーブルが出るまで待機
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "table.result-data_table_sp tbody tr"))
    )

    soup = BeautifulSoup(driver.page_source, "html.parser")
    rows = soup.select("table.result-data_table_sp tbody tr")

    data = []
    for tr in rows:
        cols = tr.find_all("td")
        # ヘッダー行など td が足りない行はスキップ
        if len(cols) < 4:
            continue

        # 学部等を取得・フィルタ
        department = cols[0].get_text(strip=True)
        if department != "理工学部数理・情報部門":
            continue

        # 条件を満たす行だけ処理
        name = cols[1].get_text(strip=True)
        link_tag = cols[3].find("a", class_="button_kenkyuu")
        research_link = link_tag["href"] if link_tag else None

        data.append({
            "department": department,
            "name": name,
            "research_link": research_link
        })

    # JSON に書き出し
    with open("saga_rikogakukei_filtered.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"フィルタ後取得件数: {len(data)} 件 → saga_rikogakukei_filtered.json に保存しました")

finally:
    driver.quit()
