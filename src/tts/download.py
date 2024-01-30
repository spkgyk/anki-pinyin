import os
import shutil

from time import sleep
from pathlib import Path
from hashlib import sha256
from selenium.webdriver.common.by import By
from selenium.webdriver import Edge, EdgeOptions
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select, WebDriverWait

from aqt import mw

from ..utils import TTS_DIR, DATA_DIR
from ..user_messages import get_progress_bar_widget


class TTSDownloader:
    web_page = "https://micmonster.com/"
    test_area_selector = "#app > div:nth-child(1) > section > div:nth-child(2) > textarea"
    generate_button_selector = "#app > div:nth-child(1) > section > div:nth-child(2) > div.row-center-between.mt-2 > button"
    audio_ready_selector = (
        "#app > div:nth-child(1) > section > div.container.upgrade-section > div.card.text-center.mx-auto.p-5.border-0 > h3"
    )
    download_button_selector = (
        "#app > div:nth-child(1) > section > div.container.upgrade-section > div.card.text-center.mx-auto.p-5.border-0 > button"
    )
    generate_more_selector = (
        "#app > div:nth-child(1) > section > div.container.upgrade-section > div.card.text-center.mx-auto.p-5.border-0 > a"
    )

    def __init__(self):
        self.download_directory = DATA_DIR / "audio"

        options = EdgeOptions()
        options.add_argument("--headless")
        options.add_argument("window-size=1920,1080")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--enable-chrome-browser-cloud-management")
        options.add_experimental_option("prefs", {"download.default_directory": str(self.download_directory)})

        service = Service(executable_path=str(TTS_DIR / "msedgedriver.exe"))

        self.driver = Edge(options, service)
        self.driver.get(TTSDownloader.web_page)

    def tts_download(self, text: str):
        progress_widget, bar = get_progress_bar_widget(4)

        # start the progress bar
        bar.setValue(0)
        mw.app.processEvents()

        # find the elements
        language_dropdown = self.driver.find_element(By.ID, "languages")
        voices_dropdown = self.driver.find_element(By.ID, "voices")
        text_area = self.driver.find_element(By.CSS_SELECTOR, TTSDownloader.test_area_selector)
        generate_button = self.driver.find_element(By.CSS_SELECTOR, TTSDownloader.generate_button_selector)

        # set language and voice
        language_dropdown_select = Select(language_dropdown)
        language_dropdown_select.select_by_value("zh-CN")
        voices_dropdown_select = Select(voices_dropdown)
        voices_dropdown_select.select_by_value("zh-CN-XiaoqiuNeural")

        # send text to micmonster
        text_area.send_keys(text)
        bar.setValue(1)
        mw.app.processEvents()

        # generate audio for text
        generate_button.click()
        wait = WebDriverWait(self.driver, 20)
        wait.until(
            expected_conditions.text_to_be_present_in_element(
                (By.CSS_SELECTOR, TTSDownloader.audio_ready_selector),
                "Your Audio is Ready",
            )
        )
        bar.setValue(2)
        mw.app.processEvents()

        # download audio file
        all_files = os.listdir(self.download_directory)
        download_button = self.driver.find_element(By.CSS_SELECTOR, TTSDownloader.download_button_selector)
        download_button.click()
        filename = self.download_directory / "zh-CN-XiaoqiuNeural{}.mp3".format(f" ({len(all_files)})" if len(all_files) else "")
        while not filename.exists():
            sleep(0.1)
        bar.setValue(3)
        mw.app.processEvents()

        # return to homepage
        return_button = self.driver.find_element(By.CSS_SELECTOR, TTSDownloader.generate_more_selector)
        return_button.click()
        wait = WebDriverWait(self.driver, 20)
        wait.until(expected_conditions.presence_of_element_located((By.ID, "languages")))
        bar.setValue(4)
        mw.app.processEvents()

        # move file to anki media folder
        hasher = sha256()
        with filename.open("rb") as audio_file:
            hasher.update(audio_file.read())
        hashed_filename = f"{hasher.hexdigest()}.mp3"
        destination_path = Path(mw.col.media.dir()) / hashed_filename
        shutil.copyfile(filename, destination_path)
        audio_tag = f"[sound:{hashed_filename}]"

        # remove temp file
        if filename.exists():
            os.remove(filename)

        mw.progress.finish()

        return audio_tag

    def close(self):
        self.driver.quit()
