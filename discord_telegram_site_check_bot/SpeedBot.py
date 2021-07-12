import asyncio

import discord

from Observer import Observer
from discord_telegram_site_check_bot.command.base.Command import Command


class DiscordChecker(discord.Client, Observer):
    def __init__(self, prefix: str, white_list: [str]):
        super().__init__()
        self.white_list = white_list
        self.commands = {}
        self.prefix = prefix

    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return
        if message.author.id in self.white_list:

            text = message.content

            if not text.startswith(self.prefix):
                return
            text = text[len(self.prefix):]
            splited_args = text.split()
            cmd = text.split()[0]

            if cmd not in self.commands:
                return
            if len(splited_args) > 1:
                args = splited_args[1:]
            else:
                args = []
            loop = asyncio.get_event_loop()

            def test(msg, embed=None):
                loop.create_task(message.channel.send(msg, embed=embed))

            if self.commands[cmd].execute is not None:
                self.commands[cmd].execute(test, args)

    def update(self, check_res):
        ...

    def get_tuple(self):
        return self.commands

    def register_command(self, command: Command):
        self.commands[command.get_name()] = command
