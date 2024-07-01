from selenium import webdriver # класс управления браузером
from selenium.webdriver.chrome.options import Options # Настройки
from selenium.webdriver.common.by import By # селекторы
from selenium.webdriver.support.ui import WebDriverWait # класс для ожидания
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
from datetime import datetime, timedelta, date
import pandas as pd
import pygsheets
import os
import shutil


SPREADSHEET = 'report_names_url'
WORKSHEET = 'reports'

LOGIN = "some_login"
PASSWORD = "some_password"

MONTHS = {1: "Jan",
          2: "Feb",
          3: "Mar",
          4: "Apr",
          5: "May",
          6: "Jun",
          7: "Jul",
          8: "Aug",
          9: "Sep",
          10: "Oct",
          11: "Nov",
          12: "Dec"}

DOWNLOAD_PATH = './all_files'
COHORT_PATH = './cohorts'
RETENTION_PATH = './retention'


def get_report_names(spreadsheet_url: str, worksheet_title: str) -> list:
    gc = pygsheets.authorize()
    sh = gc.open_by_url(spreadsheet_url)
    wk = sh.worksheet_by_title(worksheet_title)

    df_reps = wk.get_as_df(has_headers=True)
    df_reps = df_reps[df_reps['offer'] != '']

    cohort = list(set(df_reps['cohort_report'].unique()))
    retention = list(set(df_reps['retention_report'].unique()))

    return cohort, retention


def get_dates(months_literals: dict, report_name: str) -> dict:
    curr_date = datetime.now()

    if curr_date.day == 1:
        curr_date = curr_date - timedelta(days=1)
    
    curr_year = str(curr_date.year)
    curr_month = MONTHS[curr_date.month]
    curr_day = str(curr_date.day)

    start_date = f'{curr_month} 1, {curr_year}'

    if ('retention' in report_name) and (datetime.now().day != 1):
        end_date = f'{curr_month} {curr_date.day - 1}, {curr_year}'
    else:
        end_date = f'{curr_month} {curr_day}, {curr_year}'

    days = int(curr_date.day)

    return {'start_date': start_date, 'end_date': end_date, 'days': days}


def folder_clear(folder_path: str):
    list_of_files = list(map(lambda x: folder_path + x, os.listdir(folder_path)))
    for f in list_of_files:
        os.remove(f)


def rename_files(folder_path: str, report_name: str):
    list_of_files = list(map(lambda x: folder_path + x, os.listdir(folder_path)))
    list_of_files = [i for i in list_of_files if ('cohort' not in i) or ('retention' not in i)]
    latest_file = max(list_of_files, key=os.path.getctime)
    new_file = os.path.join(DOWNLOAD_PATH, f'{report_name}.csv')
    os.rename(latest_file, new_file)


# define driver parameters
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
link = "https://hq1.appsflyer.com/auth/login"
prefs = {"download.default_directory": DOWNLOAD_PATH}

chrome_option = Options()
chrome_option.add_argument(f'{user_agent=}')
chrome_option.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(options=chrome_option)
driver.get(link)

# insert login
login_form = driver.find_element(By.XPATH, "(.//input[@placeholder = 'E-mail'])[1]")
login_form.send_keys(LOGIN)

# insert password
password_form = driver.find_element(By.XPATH, "(.//input[@placeholder = 'Password'])[1]")
password_form.send_keys(PASSWORD)
time.sleep(2)

# log in
login_button = driver.find_element(By.XPATH, "(.//button[@type = 'submit'])[1]")
login_button.click()

# waiting for page to load
WebDriverWait(driver, timeout=60).until(EC.presence_of_all_elements_located((By.XPATH, './/*[@id="app"]/div/div/div[1]/div[2]/div/div/div[2]')))

# go target reports page
## dropdown menu
dd_menu = driver.find_element(By.XPATH, ".//li[@data-qa-id = 'side-menu-section-analyze-section--menu-item']")
dd_menu.click()
time.sleep(1)

## Cohort & Retention report page
cohort_report = driver.find_element(By.XPATH, ".//a[@name = 'Cohort & Retention']")
cohort_report.click()

WebDriverWait(driver, timeout=60).until(EC.presence_of_all_elements_located((By.XPATH, "(.//span/input)[1]")))

# close some popup notifications if exist
while True:
    try: 
        close_button = driver.find_element(By.XPATH, ".//button[@aria-label = 'Close']")
        close_button.click()
        time.sleep(2)
    except: 
        break

# find target report
print('--- COHORT ---')
report_names = get_report_names(SPREADSHEET, WORKSHEET)[0]
for rep in report_names:
    print(f'go for {rep}')

    # choose target report
    report_form = driver.find_element(By.XPATH, ".//div[@role = 'combobox']")
    report_form.click()
    report = driver.find_element(By.XPATH, f".//div[@role = 'option' and child::div[@data-title = '{rep}']]")
    report.click()

    # choose dates
    calendar_dropdown = driver.find_element(By.XPATH, ".//button[@data-qa-id='date-range-picker-button']")
    calendar_dropdown.click()

    from_dt = driver.find_element(By.XPATH, f".//button[@aria-label = '{get_dates(MONTHS, rep)['start_date']}']")
    from_dt.click()
    time.sleep(1)

    to_dt = driver.find_element(By.XPATH, f".//button[@aria-label = '{get_dates(MONTHS, rep)['end_date']}']")
    to_dt.click()
    time.sleep(1)

    apply_dates = driver.find_element(By.XPATH, ".//button[@data-qa-id='button-apply-date-range-picker']")
    apply_dates.click()

    # check if all cohort days are selected, otherwise select all
    selection_days = driver.find_element(By.XPATH, ".//button[@data-qa-id = 'chip-selection-days']")
    selection_days.click()
    time.sleep(1)

    select_all = driver.find_element(By.XPATH, ".//div[@role = 'button' and @data-qa-id = 'select-all']")
    select_all.click()

    if select_all.get_attribute('data-qa-state') != 'indeterminate':
        select_all.click()
        select_all.send_keys(Keys.ENTER)
    else:
        select_all.send_keys(Keys.ENTER)
    time.sleep(2)

    # download_report
    WebDriverWait(driver, timeout=20).until(EC.presence_of_all_elements_located((By.XPATH, ".//div[@class = 'table-and-chart-container']")))
    download = driver.find_element(By.XPATH, ".//button[@data-qa-id = 'export-csv-button']")
    download.click()
    time.sleep(10)
    print(f'{rep} - done')
print()


files = os.listdir(DOWNLOAD_PATH)
files = [os.path.join(DOWNLOAD_PATH, f) for f in files if os.path.isfile(os.path.join(DOWNLOAD_PATH, f))]

for f in files:
    shutil.move(f, f.replace(DOWNLOAD_PATH, COHORT_PATH))

# find target report
print('--- RETENTION ---')
report_names = get_report_names(SPREADSHEET, WORKSHEET)[1]
for rep in report_names:
    print(f'go for {rep}')

    # choose target report
    report_form = driver.find_element(By.XPATH, ".//div[@role = 'combobox']")
    report_form.click()
    report = driver.find_element(By.XPATH, f".//div[@role = 'option' and child::div[@data-title = '{rep}']]")
    report.click()

    # choose dates
    calendar_dropdown = driver.find_element(By.XPATH, ".//button[@data-qa-id='date-range-picker-button']")
    calendar_dropdown.click()

    from_dt = driver.find_element(By.XPATH, f".//button[@aria-label = '{get_dates(MONTHS, rep)['start_date']}']")
    from_dt.click()
    time.sleep(1)

    to_dt = driver.find_element(By.XPATH, f".//button[@aria-label = '{get_dates(MONTHS, rep)['end_date']}']")
    to_dt.click()
    time.sleep(1)

    apply_dates = driver.find_element(By.XPATH, ".//button[@data-qa-id='button-apply-date-range-picker']")
    apply_dates.click()

    # check if all cohort days are selected, otherwise select all
    selection_days = driver.find_element(By.XPATH, ".//button[@data-qa-id = 'chip-selection-days']")
    selection_days.click()
    time.sleep(1)

    select_all = driver.find_element(By.XPATH, ".//div[@role = 'button' and @data-qa-id = 'select-all']")
    select_all.click()

    if select_all.get_attribute('data-qa-state') != 'indeterminate':
        select_all.click()
        select_all.send_keys(Keys.ENTER)
    else:
        select_all.send_keys(Keys.ENTER)
    time.sleep(2)

    # download_report
    WebDriverWait(driver, timeout=20).until(EC.presence_of_all_elements_located((By.XPATH, ".//div[@class = 'table-and-chart-container']")))
    download = driver.find_element(By.XPATH, ".//button[@data-qa-id = 'export-csv-button']")
    download.click()
    time.sleep(10)
    print(f'{rep} - done')


files = os.listdir(DOWNLOAD_PATH)
files = [os.path.join(DOWNLOAD_PATH, f) for f in files if os.path.isfile(os.path.join(DOWNLOAD_PATH, f))]

for f in files:
    shutil.move(f, f.replace(DOWNLOAD_PATH, RETENTION_PATH))

driver.quit()