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
        self.driver.get("https://micmonster.com/")

    def tts_download(self, text: str):
        progress_widget, bar = get_progress_bar_widget(10)
        bar.setValue(0)
        mw.app.processEvents()

        language_dropdown = self.driver.find_element(By.ID, "languages")
        bar.setValue(1)
        mw.app.processEvents()

        voices_dropdown = self.driver.find_element(By.ID, "voices")
        bar.setValue(2)
        mw.app.processEvents()

        text_area = self.driver.find_element(By.XPATH, "/html/body/div[1]/section/div[2]/textarea")
        bar.setValue(3)
        mw.app.processEvents()

        generate_button = self.driver.find_element(By.XPATH, "/html/body/div[1]/section/div[2]/div[5]/button")
        bar.setValue(4)
        mw.app.processEvents()

        language_dropdown_select = Select(language_dropdown)
        language_dropdown_select.select_by_value("zh-CN")
        bar.setValue(5)
        mw.app.processEvents()

        voices_dropdown_select = Select(voices_dropdown)
        voices_dropdown_select.select_by_value("zh-CN-XiaoqiuNeural")
        bar.setValue(6)
        mw.app.processEvents()

        text_area.send_keys(text)
        bar.setValue(7)
        mw.app.processEvents()

        generate_button.click()

        wait = WebDriverWait(self.driver, 20)
        wait.until(
            expected_conditions.text_to_be_present_in_element(
                (
                    By.CSS_SELECTOR,
                    "#app > div:nth-child(1) > section > div.container.upgrade-section > div.card.text-center.mx-auto.p-5.border-0 > h3",
                ),
                "Your Audio is Ready",
            )
        )
        bar.setValue(8)
        mw.app.processEvents()

        all_files = os.listdir(self.download_directory)

        download_button = self.driver.find_element(
            By.CSS_SELECTOR,
            "#app > div:nth-child(1) > section > div.container.upgrade-section > div.card.text-center.mx-auto.p-5.border-0 > button",
        )
        download_button.click()

        filename = self.download_directory / "zh-CN-XiaoqiuNeural{}.mp3".format(f" ({len(all_files)})" if len(all_files) else "")
        while not filename.exists():
            sleep(0.1)

        bar.setValue(9)
        mw.app.processEvents()

        return_button = self.driver.find_element(
            By.CSS_SELECTOR,
            "#app > div:nth-child(1) > section > div.container.upgrade-section > div.card.text-center.mx-auto.p-5.border-0 > a",
        )
        return_button.click()

        wait = WebDriverWait(self.driver, 20)
        wait.until(expected_conditions.presence_of_element_located((By.ID, "languages")))

        bar.setValue(10)
        mw.app.processEvents()

        hasher = sha256()
        with filename.open("rb") as audio_file:
            hasher.update(audio_file.read())
        hash_name = hasher.hexdigest()

        hashed_filename = f"{hash_name}.mp3"

        destination_path = Path(mw.col.media.dir()) / hashed_filename
        shutil.copyfile(filename, destination_path)

        if filename.exists():
            os.remove(filename)

        audio_tag = f"[sound:{hashed_filename}]"

        mw.progress.finish()

        return audio_tag

    def close(self):
        self.driver.quit()
