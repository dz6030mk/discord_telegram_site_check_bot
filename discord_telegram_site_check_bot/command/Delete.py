import asyncio
import threading

from discord_telegram_site_check_bot.command.base.Command import Command
from discord_telegram_site_check_bot.DbManager import UrlsBdRepository


class Delete(Command):

    def __init__(self, url_repo, prefix, bot) -> None:
        super().__init__()
        self.url_repo: UrlsBdRepository = url_repo
        self.prefix = prefix
        self.result = []
        self.t2 = None
        self.bot = bot

    def execute(self, send_func, args: [str]):
        if self.t2 is not None and self.t2.is_alive():
            return
        loop = asyncio.get_running_loop()
        self.t2 = threading.Thread(target=lambda: loop.create_task(self.delete(send_func, args)), args=())
        self.t2.start()

    async def delete(self, send_func, args):
        if len(args) == 1:
            number_1 = int(args[0])
            number = number_1 - 1
            # channel = self.bot.get_channel(self.url_repo.get_certain_record(number))
            # await channel.delete()
            if self.url_repo.delete_element_in_db(number):
                send_func('```Удалено!```')
            else:
                send_func('```Такого элемента нет```')
        else:

            send_func(f'```{self.url_repo.all_urls()}```')

    def get_name(self):
        return 'delete'

    def get_help(self):
        return ("Delete url\n" +
                "Usage: `" + self.prefix + self.get_name() + " <url>`")
