import re
import urllib2
import threading

from bs4 import BeautifulSoup


class TitleModule:
    def module_init(self, bot):
        self.hooks = []
        self.hooks.append(bot.hook_event("PRIVMSG", self.on_privmsg))

    def module_deinit(self, bot):
        for hook in self.hooks:
            bot.unhook_something(hook)

    def on_privmsg(self, bot, ln):
        sender = ln.hostmask.nick
        message = ln.params[-1]
        reply_to = sender
        if ln.params[0][0] == "#":
            reply_to = ln.params[0]
        match = re.match(".*(http(s)?://[^ ]+).*", message)
        if match:
            url = match.group(1)
            t = TitleFetchThread(url, lambda resp: bot.privmsg(reply_to, resp), self)
            t.start()


class TitleFetchThread(threading.Thread):
    def __init__(self, url, reply_func, module):
        super(TitleFetchThread, self).__init__()
        self.url = url
        self.reply_func = reply_func
        self.module = module

    def run(self):
        try:
            data = urllib2.urlopen(self.url, None, 1.5).read()
        except Exception as e:
            print("urltitle", "Error fetching title for URL '%s': %s" % (self.url, str(e)))
            return

        soup = BeautifulSoup(data)
        if hasattr(soup, "title") and soup.title is not None:
            self.reply_func("[ %s ] - %s" % (soup.title.text, self.url))