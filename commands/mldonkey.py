# -*- coding: utf-8 -*-
import sys
from telnetlib import Telnet
from base import BaseCommand
from optparse import OptionParser
from db import Episode, Show

class MLException(Exception):
    pass

class MLAuthException(MLException):
    pass

class MLURLException(MLException):
    pass

class Command(BaseCommand):
    def create_parser(self):
        parser = OptionParser(usage="mldonkey")
        self.parser = parser

        parser.set_defaults(host='', port=0, user="", passwd="")
        parser.add_option("-m", "--host", dest="host",
                help="hostname", metavar="HOST")
        parser.add_option("-p", "--port", dest="port", type="int",
                help="port", metavar="PORT")
        parser.add_option("-u", "--user", dest="user",
                help="user", metavar="USER")
        parser.add_option("-w", "--password", dest="passwd",
                help="password", metavar="PASSWORD")
        return parser

    def _best_value(self, opt, config_var, default):
        if opt:
            return opt

        tmp = self.get_config(config_var)
        if tmp:
            return tmp

        return default

    def check_args(self, args):
        (self.options, _) = self.parser.parse_args(args)

        self.username = self._best_value(self.options.user, "mldonkey.username", "admin")
        self.passwd = self._best_value(self.options.passwd, "mldonkey.password", "")
        self.host = self._best_value(self.options.host, "mldonkey.host", "localhost")
        self.port = self._best_value(self.options.port, "mldonkey.port", 4000)

        return True

    def _send_command(self, torrent):
        telnet = Telnet()
        telnet.open(self.host, int(self.port))
        try:
            telnet.read_until(">")
            telnet.write("auth %s %s\n" % (str(self.username), str(self.passwd)))
            telnet.read_until(">")
            telnet.write("dllink %s\n" % str(torrent))
            telnet.write("quit\n")
            session = telnet.read_all()
            #print session
            if "Bad login" in session:
                raise MLAuthException
            elif "exception" in session:
                raise MLURLException

        finally:
            telnet.close()

    def run(self):
        episodes = self.store.find(Episode, Episode.queued == False, Episode.downloaded == False)

        if episodes.count() <= 0:
            print "No pending episodes in DB. Exiting."
            return

        for episode in episodes:
            print u"Sending %s to mldonkey(%s:%s)" % (unicode(episode), self.host, self.port)
            for url in episode.urls():
                try:
                    self._send_command(url)
                    episode.queued = True
                    self.store.commit()
                    print "%s OK" % unicode(episode)
                    break
                except MLAuthException:
                    print "Wrong credentials for %s:%s" % (self.host, self.port)
                    return
                except MLURLException:
                    print "%s failed. Trying next url." % url


