import os
import shutil

from io import StringIO
from pathlib import Path
from hashlib import sha256
from threading import Lock
from time import sleep, time
from html.parser import HTMLParser
from selenium.webdriver.common.by import By
from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select, WebDriverWait

from aqt import mw

from ..utils import TTS_DIR, AUDIO_DIR
from ..user_messages import get_progress_bar_widget


MKDIR_LOCK = Lock()


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

    def __init__(self, worker: int, media_dir: Path):
        self.worker = worker
        self.media_dir = media_dir
        self.download_dir = AUDIO_DIR / f"worker_{self.worker}"
        with MKDIR_LOCK:
            os.makedirs(self.download_dir)
        self._get_webpage()

    def _get_webpage(self):
        options = FirefoxOptions()
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.dir", str(self.download_dir))
        options.set_preference("browser.download.manager.showWhenStarting", False)
        options.set_preference("browser.helperApps.neverAsk.saveToDisk", "audio/mpeg")

        service = Service(executable_path=str(TTS_DIR / "geckodriver.exe"))

        self.driver = Firefox(options, service)
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
                    raise

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
        wait = WebDriverWait(self.driver, 30)
        wait.until(
            expected_conditions.text_to_be_present_in_element(
                (By.CSS_SELECTOR, TTSDownloader.audio_ready_selector),
                "Your Audio is Ready",
            )
        )
        if progress_bar:
            bar.setValue(2)
            mw.app.processEvents()

        # get current number of files, then download audio file
        current_file_count = len(os.listdir(self.download_dir))
        download_button = self.driver.find_element(By.CSS_SELECTOR, TTSDownloader.download_button_selector)
        download_button.click()

        # wait for download for at most 10 seconds
        start_time = time()
        while (len(os.listdir(self.download_dir)) == current_file_count) or (time() - start_time < 10):
            sleep(0.1)

        # retrieve latest file
        latest_file = max(os.listdir(self.download_dir), key=lambda filename: os.path.getctime(self.download_dir / filename))
        filename = self.download_dir / latest_file

        # make sure its an mp3...
        assert latest_file.endswith("mp3")
        if progress_bar:
            bar.setValue(3)
            mw.app.processEvents()

        # return to homepage
        return_button = self.driver.find_element(By.CSS_SELECTOR, TTSDownloader.generate_more_selector)
        return_button.click()
        wait = WebDriverWait(self.driver, 30)
        wait.until(expected_conditions.presence_of_element_located((By.ID, "languages")))
        if progress_bar:
            bar.setValue(4)
            mw.app.processEvents()

        # move file to anki media folder
        hasher = sha256()
        with filename.open("rb") as audio_file:
            hasher.update(audio_file.read())
        hashed_filename = f"{hasher.hexdigest()}.mp3"
        destination_path = self.media_dir / hashed_filename
        shutil.copyfile(filename, destination_path)
        audio_tag = f"[sound:{hashed_filename}]"

        if progress_bar:
            mw.progress.finish()

        return audio_tag

    def close(self):
        self.driver.quit()
