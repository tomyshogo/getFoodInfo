import bs4
import traceback
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
 
 
# ドライバーのフルパス
CHROMEDRIVER = "/Users/tomyshogo/Documents/dev/Python_application/飲食店情報/chromedriver-mac-x64"
# 改ページ（最大）
PAGE_MAX = 1
# 遷移間隔（秒）
INTERVAL_TIME = 3
 
 
# ドライバー準備
def get_driver():
    # # ヘッドレスモードでブラウザを起動
    options = Options()
    # options.add_argument('--headless')
 
    # # ブラウザーを起動
    # driver = webdriver.Chrome(CHROMEDRIVER, options=options)
    # optionsを設定
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")

    # Serviceオブジェクトを作成し、その引数にChromeDriverManager().install()を渡す
    service = Service(ChromeDriverManager().install())
    # webdriver.Chromeの呼び出し時にserviceとoptionsを渡す
    driver = webdriver.Chrome(service=service, options=options)
    return driver
 
 
# 対象ページのソース取得
def get_source_from_page(driver, page):
    try:
        # ターゲット
        driver.get(page)
        driver.implicitly_wait(10)  # 見つからないときは、10秒まで待つ
        page_source = driver.page_source
 
        return page_source
 
    except Exception as e:
 
        print("Exception\n" + traceback.format_exc())
 
        return None
 
 
# ソースからスクレイピングする
def get_data_from_source(src):
    # スクレイピングする
    soup = bs4.BeautifulSoup(src, features='lxml')
 
    try:
        info = []
        elems = soup.find_all(class_="list-rst")
 
        for elem in elems:
 
            shop = {}
            shop["rank"] = None
            shop["name"] = None
            shop["area"] = None
            shop["genre"] = None
            shop["star"] = None
            # shop["rvw_count"] = None
            shop["dinner_budget"] = None
            shop["lunch_budget"] = None
            shop["holiday_data"] = None
            # shop["search_word"] = None
 
            # 順位
            rank = elem.find(class_="list-rst__rank-badge-no")
            if rank is None:
                continue
            if rank:
                shop["rank"] = rank.text
 
            # 店舗名
            name = elem.find(class_="list-rst__rst-name-target").text
            if name:
                shop["name"] = name
 
            # 地域とジャンル
            area_genre = elem.find(class_="list-rst__area-genre").text
            if area_genre:
                area_genre_list = area_genre.split("/")
                if len(area_genre_list) == 2:
                    shop["area"] = my_trim(area_genre_list[0])
 
                    tmp_genre = area_genre_list[1]
                    tmp_genre_list = tmp_genre.split("、")
                    genre_list = []
                    for genre in tmp_genre_list:
                        genre_list.append(my_trim(genre))
                    shop["genre"] = genre_list
 
            # 評価
            star = elem.find(class_="list-rst__rating-val").text
            if star:
                shop["star"] = star
 
            # # 評価
            # rvw_count = elem.find(class_="list-rst__rvw-count-num").text
            # if rvw_count:
            #     shop["rvw_count"] = rvw_count
 
            # 予算
            budget_elems = elem.find_all(class_="list-rst__budget-val")
            if len(budget_elems) == 2:
                shop["dinner_budget"] = budget_elems[0].text
                shop["lunch_budget"] = budget_elems[1].text
 
 
            # 休日
            if elem.find(class_="list-rst__holiday"):
                holiday_data = elem.find(class_="list-rst__holiday-datatxt").text
                if holiday_data:
                    shop["holiday_data"] = holiday_data
 
            # # 検索キーワード
            # search_word_elems = elem.find_all(class_="list-rst__search-word-item")
 
            # if len(search_word_elems) > 0:
            #     search_word_list = []
            #     for search_word_elem in search_word_elems:
            #         search_word = search_word_elem.text
            #         if my_trim(search_word):
            #             search_word_list.append(my_trim(search_word))
            #     shop["search_word"] = search_word_list
 
            # # 画像
            # if elem.find(class_="list-rst__rst-photo"):
            #     photo_set_str = elem.find(class_="list-rst__rst-photo").attrs['data-photo-set']
 
            #     if photo_set_str:
            #         tmp_photo_set = photo_set_str.split("、")
            #         img_list = []
            #         for img in tmp_photo_set:
            #             img_list.append(img)
            #         shop["img"] = img_list
 
            info.append(shop)
 
        return info
 
    except Exception as e:
 
        print("Exception\n" + traceback.format_exc())
 
        return None
 
 
# 次のページへ遷移
def next_btn_click(driver):
    try:
        # 次へボタン
        elem_btn = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "c-pagination__arrow--next"))
        )
 
        actions = ActionChains(driver)
        actions.move_to_element(elem_btn)
        actions.click(elem_btn)
        actions.perform()
 
        # 間隔を設ける(秒単位）
        time.sleep(INTERVAL_TIME)
 
        return True
 
    except Exception as e:
 
        print("Exception\n" + traceback.format_exc())
 
        return False
 
def my_trim(text):
    text = text.replace("\n", "")
    return text.strip()
 
 
if __name__ == "__main__":
    # 対象ページURL
    page = "https://tabelog.com/osaka/A2701/A270101/rstLst/izakaya/?Srt=D&amp;SrtT=rt&amp;sort_mode=1"
 
    # ブラウザのdriver取得
    driver = get_driver()
 
    # ページのソース取得
    source = get_source_from_page(driver, page)
    result_flg = True
 
    # ページカウンター制御
    page_counter = 0
 
    while result_flg:
        page_counter = page_counter + 1
 
        # ソースからデータ抽出
        data = get_data_from_source(source)
 
        # データ保存
        print(data)
 
        # 改ページ処理を抜ける
        if page_counter == PAGE_MAX:
            break
 
        # 改ページ処理
        result_flg = next_btn_click(driver)
        source = driver.page_source
 
    # 閉じる
    driver.quit()