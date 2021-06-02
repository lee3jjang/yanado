import time
import pandas as pd
from typing import List
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from rich.console import Console
from rich.traceback import install
from rich.progress import track
install()

console = Console()

# 데이터프레임 콘솔 출력
def print_dataframe(df: pd.DataFrame, title: str = None) -> None:
    from rich.table import Table
    table = Table(title=title)
    for col in df.columns:
        table.add_column(col)
    for _, row in df.iterrows():
        table.add_row(*row)
    console.print(table)

# 크롬 드라이버
driver = webdriver.Chrome(executable_path='chromedriver')

def login(id: str, pwd: str, direct_input: bool) -> None:
    url = 'https://www.yanadoo.co.kr/myclass/classroom/today'
    driver.get(url)

    if direct_input:
        id = input('Enter ID: ')
        pwd = input('Enter Password: ')

    driver.find_element_by_id('login_sub_id').send_keys(id)
    driver.find_element_by_id('login_main_pw').send_keys(pwd)
    driver.execute_script('member_loginChk()')

    # 배너 닫기
    try:
        time.sleep(5)
        driver.execute_script("$('.pop-milchak-ninetyday').hide()")
        time.sleep(1)
    except:
        pass


def get_classes_not_completed() -> pd.DataFrame:
    # [이전 구매 상품] 버튼 클릭
    driver.find_element_by_css_selector('#main > div.container > ul.tab-menu > li:nth-child(2)').click()
    # tag = driver.find_element_by_css_selector('#main > div.container > ul.tab-menu > li:nth-child(2)')
    # driver.execute_script('arguments[0].click()', tag)

    # 전체 리스트 수집
    classes_tag = driver.find_element_by_css_selector('#main > div.container > div.contents > div.tab-page > div.my-lecture > div.inner > div.class-list-box > ul.class-list') \
        .find_elements_by_tag_name('li')
    classes = []
    for tag in track(classes_tag, description='Reading classes...'):
        teacher = tag.find_element_by_css_selector('div.class-item > dl.study-name > dd > span.teacher').text
        title = tag.find_element_by_css_selector('div.class-item > dl.study-name > dd > p.title').text
        progress = tag.find_element_by_css_selector('div.class-item > dl.study-box > dd > div.progress-box > div.progress > div.progress-info > b > i').text
        progress_detail = tag.find_element_by_css_selector('div.class-item > dl.study-box > dd > div.progress-box > div.progress > div.progress-info > em').text
        url = tag.find_element_by_css_selector('a.link-classroom').get_attribute('href')
        classes.append([teacher, title, progress, progress_detail, url])
    classes_df = pd.DataFrame(classes, columns=['teacher', 'title', 'progress', 'progress_detail', 'url'])

    # 완료 강의 필터링
    classes_df = classes_df \
        .query('progress != "100"')

    return classes_df

def play_lecture(url: str) -> None:
    if url == "https://www.yanadoo.co.kr/classroom/package_study_room/12148165":
        # 강의창으로 이동
        driver.get(url)
        driver.switch_to.frame('RoomDetailFrame')
        rows = driver.find_element_by_css_selector('div.table_area > table > tbody').find_elements_by_tag_name('tr')
        for row in rows:
            if row.find_element_by_tag_name('td').get_attribute('colspan') != '4':
                if row.find_element_by_class_name('percent').text != "100%":
                    row.find_element_by_css_selector('td.btns > a:nth-child(1)').click()
                    lecture_start_num = row.find_element_by_css_selector('td.num').text[:-1]
                    break
        time.sleep(3)
        driver.switch_to.window(driver.window_handles[-1])

        # 각 강의 재생
        for num in range(int(lecture_start_num), 29):
            for arg in ['', '2_']:
                driver.execute_script(f"javascript:$('#movieForm{arg}{num}').submit()")

                time.sleep(5)

                # if 진도율 100% -> continue
                if driver.find_element_by_css_selector('#bottom > div.stdProcess > div.stdPrpersen > div.stdPsmy02').get_attribute('innerHTML') == '100%':
                    continue

                # 재생버튼 클릭
                driver.find_element_by_css_selector('#container > .movieArea').click()
                frame = driver.find_element_by_css_selector('#container > .movieArea > iframe')
                driver.switch_to.frame(frame)
                try:
                    driver.find_element_by_css_selector('#popup > div.footer > div.button-submit.button').click()
                except:
                    pass

                # 잔여시간 감시 -> break
                while True:
                    try:
                        remaining_time = driver.find_element_by_css_selector('div.vjs-remaining-time-display') \
                            .get_attribute('innerHTML')[-8:]
                        console.log(f'Remaining time is {remaining_time}')
                        if remaining_time != '-0:00:00':
                            time.sleep(10)
                        else:
                            driver.switch_to.parent_frame()
                            break
                    except NoSuchElementException:
                        driver.switch_to.parent_frame()
                        break
    



if __name__ == '__main__':
    login(None, None, direct_input=True)
    # classes = get_classes_not_completed()
    # print_dataframe(classes, title='Classes not completed')
    play_lecture('https://www.yanadoo.co.kr/classroom/package_study_room/12148165')



    # 종료
    input("Enter를 누르면 종료합니다.")
    driver.close()