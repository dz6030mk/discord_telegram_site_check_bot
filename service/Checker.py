import asyncio
import threading
import time
from typing import List

import requests

from command.enums.SiteState import SiteState
from command.utils.EncodingTime import EncoderTime
from command.utils.dataclasses.CheckResult import CheckResult
from service.DbManager import UrlsBdRepository
from service.Observer import Observer
from service.Publisher import Publisher


class Checker(Publisher):

    def __init__(self, url_repo: UrlsBdRepository) -> None:
        super().__init__()
        self.url_repo: UrlsBdRepository = url_repo
        self.t1 = None
        self.encoder = EncoderTime()
        self.loop = None
        self._observers: List[Observer] = []

    def attach(self, observer: Observer) -> None:
        print("SUBJECT attached on observer")
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def notify(self, check_res) -> None:
        print("Subject: Notifying observers...")
        for observer in self._observers:
            observer.update(check_res, self.loop)

    def start(self, time_of_checking):
        if self.t1 is not None and self.t1.is_alive():
            return False
        try:
            self.loop = asyncio.get_event_loop()
        except Exception:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        self.t1 = threading.Thread(target=lambda: self.check(time_of_checking), args=())
        self.t1.start()
        return True

    def check(self, time_of_checking: int):
        while self.url_repo.get_state() == True:

            for resource in self.url_repo.all_info():
                url = resource[0]
                old_status = resource[1]
                last_time = resource[2]
                chnl_id = resource[3]
                chnl_name = resource[4]
                category = resource[5]
                try:
                    r = requests.get(url, timeout=2)
                    status_code = r.status_code
                except Exception:
                    status_code = -1
                new_status = SiteState.READY if status_code == 200 else SiteState.NOT_READY
                data = time.time()
                if new_status.value != old_status:
                    self.url_repo.update_status(url, new_status.value, int(data))
                    if new_status == SiteState.READY:
                        date = data - last_time
                        time_of = self.encoder.encod(date)
                        check_res = CheckResult(url, time_of, status_code, new_status, old_status, chnl_id, chnl_name,
                                                category)
                        self.notify(check_res)
                    elif new_status == SiteState.NOT_READY:
                        date = data - last_time
                        time_of = self.encoder.encod(date)
                        check_res = CheckResult(url, time_of, status_code, new_status, old_status, chnl_id, chnl_name,
                                                category)
                        self.notify(check_res)

        time.sleep(int(time_of_checking))

    def fast_check(self):
        results = []
        for resource in self.url_repo.all_info():
            url = resource[0]
            old_status = resource[1]
            last_time = resource[2]
            try:
                r = requests.get(url, timeout=2)
                status_code = r.status_code
            except Exception:
                status_code = -1
            new_status = SiteState.READY if status_code == 200 else SiteState.NOT_READY
            data = time.time()
            if new_status.value != old_status:
                self.url_repo.update_status(url, new_status.value, int(data))
            if new_status == SiteState.READY:
                time_of = data - last_time
                results.append(f'🟢{url} {self.encoder.encod(time_of)}🟢')
            elif new_status == SiteState.NOT_READY:
                time_of = data - last_time
                emoji = '🟠' if status_code == -1 else '🔴'
                results.append(f'{emoji}{url} {self.encoder.encod(time_of)} ERROR = {status_code}{emoji}')
        if len(results) != 0:
            results = '\n'.join(results)
            return results
