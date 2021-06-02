from selenium import webdriver
import time
from typing import List
import pandas as pd
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

def login(id: str, pwd: str, stay_signed_in: bool) -> None:
    url = 'https://www.yanadoo.co.kr/myclass/classroom/today'
    driver.get(url)

    if stay_signed_in:
        pass
    else:
        # TODO 구현해야 함
        driver.find_element_by_id('login_sub_id').send_keys(id)
        driver.find_element_by_id('login_main_pw').send_keys(pwd)
        driver.execute_script('member_loginChk()')

        # 배너 닫기
        try:
            time.sleep(5)
            driver.execute_script("$('.pop-milchak-ninetyday').hide()")
        except:
            pass


def get_lectures_of_not_completed_lectures() -> pd.DataFrame:
    # [이전 구매 상품] 버튼 클릭
    driver.find_element_by_css_selector('#main > div.container > ul.tab-menu > li:nth-child(2)').click()
    # tag = driver.find_element_by_css_selector('#main > div.container > ul.tab-menu > li:nth-child(2)')
    # driver.execute_script('arguments[0].click()', tag)

    lectures_tag = driver.find_element_by_css_selector('#main > div.container > div.contents > div.tab-page > div.my-lecture > div.inner > div.class-list-box > ul.class-list') \
        .find_elements_by_tag_name('li')

    # 전체 리스트 수집
    lectures = []
    for tag in track(lectures_tag, description='Reading Lectures...'):
        teacher = tag.find_element_by_css_selector('div.class-item > dl.study-name > dd > span.teacher').text
        title = tag.find_element_by_css_selector('div.class-item > dl.study-name > dd > p.title').text
        progress = tag.find_element_by_css_selector('div.class-item > dl.study-box > dd > div.progress-box > div.progress > div.progress-info > b > i').text
        progress_detail = tag.find_element_by_css_selector('div.class-item > dl.study-box > dd > div.progress-box > div.progress > div.progress-info > em').text
        url = tag.find_element_by_css_selector('a.link-classroom').get_attribute('href')
        lectures.append([teacher, title, progress, progress_detail, url])
    lectures_df = pd.DataFrame(lectures, columns=['teacher', 'title', 'progress', 'progress_detail', 'url'])

    # 미완료 리스트 필터링
    lectures_df = lectures_df \
        .query('progress != "100"')
    return lectures_df





if __name__ == '__main__':
    login('xxxxxxxx', 'xxxxxxxx', False)
    lectures = get_lectures_of_not_completed_lectures()
    print_dataframe(lectures, title='Lectures not completed')

    # 종료
    input("Enter를 누르면 종료합니다.")
    driver.close()