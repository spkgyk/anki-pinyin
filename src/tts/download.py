import os
import shutil

from io import StringIO
from pathlib import Path
from hashlib import sha256
from threading import Lock
from typing import Sequence
from time import sleep, time
from html.parser import HTMLParser
from selenium.webdriver.common.by import By
from selenium.webdriver import Firefox, FirefoxOptions
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select, WebDriverWait

from aqt import mw
from aqt.qt import *
from anki.notes import NoteId

from ..tokenizer import strip_display_format
from ..user_messages import ProgressBarWidget
from ..utils import TTS_DIR, AUDIO_DIR, OutputMode, apply_output_mode


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


class WorkerSignals(QObject):
    progress = pyqtSignal(int)
    finished = pyqtSignal(dict)


class NotesProcessor(QRunnable):

    def __init__(
        self,
        worker: int,
        nid_dicts: dict[NoteId, str],
        media_dir: Path,
        progress_callable: Callable,
        finished_callable: Callable,
        cancel_connection: pyqtBoundSignal,
    ):
        super(NotesProcessor, self).__init__()
        self.signals = WorkerSignals()
        self.worker = worker
        self.nid_dicts = nid_dicts
        self.media_dir = media_dir
        self._cancel = False
        self.downloader = None
        self.signals.progress.connect(progress_callable)
        self.signals.finished.connect(finished_callable)
        cancel_connection.connect(self.cancel)

    def run(self):
        will_process = {}
        if self.nid_dicts:
            self.downloader = TTSDownloader(self.worker, self.media_dir)
            for nid, selected_text in self.nid_dicts.items():
                if self._cancel:
                    self.downloader.cancel()
                    self.downloader.close()
                    del self.downloader
                    return
                audio_tag = self.downloader.tts_download(selected_text)
                if audio_tag:
                    will_process[nid] = audio_tag
                    self.signals.progress.emit(1)
        self.signals.finished.emit(will_process)

    def cancel(self):
        if self.downloader:
            self.downloader.cancel()
        self._cancel = True


class DownloadsThreadManager(QObject):
    cancel_all_workers = pyqtSignal()

    def __init__(self, source: str, dest: str, output_mode: OutputMode, notes: Sequence[NoteId], num_workers: int):
        super(DownloadsThreadManager, self).__init__()
        self.source = source
        self.dest = dest
        self.output_mode = output_mode
        self.notes = notes
        self.num_workers = num_workers

        self.progress_widget = ProgressBarWidget(len(self.notes))

        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(self.num_workers)
        self.processed = {}
        self.media_dir = Path(mw.col.media.dir())

        self.tasks_completed = 0

        self.note_groups = [{} for _ in range(self.num_workers)]
        self.notes_to_be_processed = 0
        for i, nid in enumerate(self.notes):
            note = mw.col.get_note(nid)
            if source in note.keys() and dest in note.keys():
                self.note_groups[i % self.num_workers][nid] = strip_display_format(note[source], "cn")
                self.notes_to_be_processed += 1
            self.update_progress_bar(1)

        shutil.rmtree(AUDIO_DIR, ignore_errors=True)
        os.makedirs(AUDIO_DIR, exist_ok=True)

        self.progress_widget.close()

    def start_tasks(self):
        self.progress_widget = ProgressBarWidget(self.notes_to_be_processed, True)
        self.progress_widget.cancel_connect(self.cancel)
        for worker, nid_dicts in enumerate(self.note_groups):
            note_processor_worker = NotesProcessor(
                worker,
                nid_dicts,
                self.media_dir,
                self.update_progress_bar,
                self.task_finished,
                self.cancel_all_workers,
            )
            self.threadpool.start(note_processor_worker)

    def update_progress_bar(self, value: int):
        self.progress_widget.increment_value(value)

    def task_finished(self, result: dict[NoteId, str]):
        self.processed.update(result)
        self.tasks_completed += 1
        self.check_all_tasks_completed()

    def check_all_tasks_completed(self):
        if self.tasks_completed == self.num_workers:
            self.progress_widget.close()
            self.all_tasks_finished()

    def all_tasks_finished(self):
        self.progress_widget = ProgressBarWidget(self.notes_to_be_processed)
        shutil.rmtree(AUDIO_DIR, ignore_errors=True)
        os.makedirs(AUDIO_DIR, exist_ok=True)
        for nid, text in self.processed.items():
            note = mw.col.get_note(nid)
            note[self.dest] = apply_output_mode(self.output_mode, note[self.dest], text)
            mw.col.update_note(note)
            self.update_progress_bar(1)

        self.progress_widget.close()
        mw.manager = None

    def cancel(self):
        self.cancel_all_workers.emit()
        self.threadpool.start(self.clear_up)

    def clear_up(self):
        shutil.rmtree(AUDIO_DIR, ignore_errors=True)
        os.makedirs(AUDIO_DIR, exist_ok=True)
        self.progress_widget.close()
        mw.manager = None


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
        self._cancel = False
        with MKDIR_LOCK:
            os.makedirs(self.download_dir, exist_ok=True)
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
                if attempt > 0:
                    self._get_webpage()
                return self._download(text, progress_bar)
            except Exception as e:
                self.close()
                if self._cancel:
                    return False
                if attempt == number_of_attempts - 1:
                    return False

    def _find_elements(self, progress_bar: bool):
        if progress_bar:
            self.progress_widget = ProgressBarWidget(4)

        # start the progress bar
        if progress_bar:
            self.progress_widget.set_value(0)

        # find the elements
        self.language_dropdown = self.driver.find_element(By.ID, "languages")
        self.voices_dropdown = self.driver.find_element(By.ID, "voices")
        self.text_area = self.driver.find_element(By.CSS_SELECTOR, TTSDownloader.test_area_selector)
        self.generate_button = self.driver.find_element(By.CSS_SELECTOR, TTSDownloader.generate_button_selector)

    def _set_language_and_voice(self):
        # set language and voice
        self.language_dropdown_select = Select(self.language_dropdown)
        self.language_dropdown_select.select_by_value("zh-CN")
        self.voices_dropdown_select = Select(self.voices_dropdown)
        self.voices_dropdown_select.select_by_value("zh-CN-XiaoqiuNeural")

    def _send_text(self, text: str, progress_bar: bool):
        # send text to micmonster
        self.text_area.clear()
        self.text_area.send_keys(text)
        if progress_bar:
            self.progress_widget.set_value(1)

    def _generate_audio(self, progress_bar: bool):
        # generate audio for text
        self.generate_button.click()
        wait = WebDriverWait(self.driver, 30)
        wait.until(
            expected_conditions.text_to_be_present_in_element(
                (By.CSS_SELECTOR, TTSDownloader.audio_ready_selector),
                "Your Audio is Ready",
            )
        )
        if progress_bar:
            self.progress_widget.set_value(2)

    def _download_audio_file(self, progress_bar: bool):
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
            self.progress_widget.set_value(3)

        return filename

    def _return_to_homepage(self, progress_bar: bool):
        return_button = self.driver.find_element(By.CSS_SELECTOR, TTSDownloader.generate_more_selector)
        return_button.click()
        wait = WebDriverWait(self.driver, 30)
        wait.until(expected_conditions.presence_of_element_located((By.ID, "languages")))
        if progress_bar:
            self.progress_widget.set_value(4)

    def _move_download_and_get_audio_tag(self, filename: Path, progress_bar: bool):
        # move file to anki media folder
        hasher = sha256()
        with filename.open("rb") as audio_file:
            hasher.update(audio_file.read())
        hashed_filename = f"zh-CN-XiaoqiuNeural-{hasher.hexdigest()}.mp3"
        destination_path = self.media_dir / hashed_filename
        shutil.copyfile(filename, destination_path)
        audio_tag = f"[sound:{hashed_filename}]"

        if progress_bar:
            self.progress_widget.close()

        return audio_tag

    def _download(self, text: str, progress_bar: bool = False):

        self._find_elements(progress_bar)
        self._set_language_and_voice()
        self._send_text(text, progress_bar)
        self._generate_audio(progress_bar)
        filename = self._download_audio_file(progress_bar)
        self._return_to_homepage(progress_bar)
        audio_tag = self._move_download_and_get_audio_tag(filename, progress_bar)

        return audio_tag

    def cancel(self):
        self._cancel = True

    def close(self):
        try:
            self.driver.quit()
        except:
            pass
