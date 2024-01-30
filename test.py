# from src.tokenizer.chinese import ChineseTokenizer
# from src.utils import ReadingType

# cn_text = "我25岁。"
# ct = ChineseTokenizer()
# x = ct.tokenize(cn_text, ReadingType.JYUTPING)
# [print(token) for token in x]

# print(ct.gen_display_format(cn_text, ReadingType.JYUTPING).traditional)

import os
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver import Edge, EdgeOptions
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select, WebDriverWait
from src.utils import TTS_DIR, DATA_DIR

download_directory = DATA_DIR / "audio"

options = EdgeOptions()
options.add_argument("--enable-chrome-browser-cloud-management")
options.add_argument("--disable-popup-blocking")  # Disable the file download dialog
options.add_experimental_option("prefs", {"download.default_directory": str(download_directory)})

service = Service(executable_path=str(TTS_DIR / "msedgedriver.exe"))

driver = Edge(options, service)
driver.get("https://micmonster.com/")

language_dropdown = driver.find_element(By.ID, "languages")
voices_dropdown = driver.find_element(By.ID, "voices")
text_area = driver.find_element(By.XPATH, "/html/body/div[1]/section/div[2]/textarea")
generate_button = driver.find_element(By.XPATH, "/html/body/div[1]/section/div[2]/div[5]/button")

language_dropdown_select = Select(language_dropdown)
language_dropdown_select.select_by_value("zh-CN")

voices_dropdown_select = Select(voices_dropdown)
voices_dropdown_select.select_by_value("zh-CN-XiaoqiuNeural")

text_area.send_keys("你好")

generate_button.click()

wait = WebDriverWait(driver, 20)
wait.until(
    expected_conditions.text_to_be_present_in_element(
        (
            By.CSS_SELECTOR,
            "#app > div:nth-child(1) > section > div.container.upgrade-section > div.card.text-center.mx-auto.p-5.border-0 > h3",
        ),
        "Your Audio is Ready",
    )
)

all_files = os.listdir(download_directory)

download_button = driver.find_element(
    By.CSS_SELECTOR,
    "#app > div:nth-child(1) > section > div.container.upgrade-section > div.card.text-center.mx-auto.p-5.border-0 > button",
)
download_button.click()


filename = "zh-CN-XiaoqiuNeural{}.mp3".format(f" ({len(all_files)})" if len(all_files) else "")
while not (download_directory / filename).exists():
    sleep(0.1)

return_button = driver.find_element(
    By.CSS_SELECTOR, "#app > div:nth-child(1) > section > div.container.upgrade-section > div.card.text-center.mx-auto.p-5.border-0 > a"
)
return_button.click()

wait = WebDriverWait(driver, 20)
wait.until(expected_conditions.presence_of_element_located((By.ID, "languages")))


driver.quit()
