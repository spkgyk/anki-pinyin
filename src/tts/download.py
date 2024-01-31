import os
import shutil

from io import StringIO
from pathlib import Path
from hashlib import sha256
from threading import Lock
from time import sleep, time
from html.parser import HTMLParser
from selenium.webdriver.common.by import By
from selenium.webdriver import Edge, EdgeOptions
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select, WebDriverWait

from aqt import mw
from aqt.utils import showInfo

from ..utils import TTS_DIR, AUDIO_DIR
from ..user_messages import get_progress_bar_widget


DOWNLOAD_LOCK = Lock()


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


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
        self._get_webpage()

    def _get_webpage(self):
        options = EdgeOptions()
        # options.add_argument("--headless")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--enable-chrome-browser-cloud-management")
        options.add_experimental_option("prefs", {"download.default_directory": str(AUDIO_DIR)})

        service = Service(executable_path=str(TTS_DIR / "msedgedriver.exe"))

        self.driver = Edge(options, service)
        self.driver.get(TTSDownloader.web_page)

    def tts_download(self, text: str, progress_bar=False, number_of_attempts=5):
        text = strip_tags(text)

        for attempt in range(number_of_attempts):
            try:
                return self._download(text, progress_bar)
            except Exception as e:
                if attempt < number_of_attempts - 1:
                    self.close()
                    self._get_webpage()
                else:
                    showInfo(f"Attempt {attempt + 1} failed: {e}\nText: {text}")

    def _download(self, text: str, progress_bar=False):
        if progress_bar:
            progress_widget, bar = get_progress_bar_widget(4)

        # start the progress bar
        if progress_bar:
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
        text_area.clear()
        text_area.send_keys(text)
        if progress_bar:
            bar.setValue(1)
        mw.app.processEvents()

        # generate audio for text
        generate_button.click()
        wait = WebDriverWait(self.driver, 40)
        wait.until(
            expected_conditions.text_to_be_present_in_element(
                (By.CSS_SELECTOR, TTSDownloader.audio_ready_selector),
                "Your Audio is Ready",
            )
        )
        if progress_bar:
            bar.setValue(2)
        mw.app.processEvents()

        # download audio file
        with DOWNLOAD_LOCK:
            start_time = time()
            files = len(os.listdir(AUDIO_DIR))
            download_button = self.driver.find_element(By.CSS_SELECTOR, TTSDownloader.download_button_selector)
            download_button.click()

            # wait for download to start
            while (len(os.listdir(AUDIO_DIR)) == files) or self._check_for_downloads() or (time() - start_time < 10):
                sleep(0.1)

            latest_file = max(os.listdir(AUDIO_DIR), key=lambda x: os.path.getctime(AUDIO_DIR / x))
            assert latest_file.endswith("mp3")
            filename = AUDIO_DIR / latest_file
        if progress_bar:
            bar.setValue(3)
        mw.app.processEvents()

        # move file to anki media folder
        hasher = sha256()
        with filename.open("rb") as audio_file:
            hasher.update(audio_file.read())
        hashed_filename = f"{hasher.hexdigest()}.mp3"
        destination_path = Path(mw.col.media.dir()) / hashed_filename
        shutil.copyfile(filename, destination_path)
        audio_tag = f"[sound:{hashed_filename}]"

        if progress_bar:
            mw.progress.finish()

        return audio_tag

    def _check_for_downloads(self):
        return [f for f in os.listdir(AUDIO_DIR) if not f.endswith(".mp3")]

    def close(self):
        self.driver.quit()
