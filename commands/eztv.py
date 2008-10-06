import re
import sys
from base import BaseCommand
from optparse import OptionParser
from eztvefnet import Scrapper
from db import Show, Episode

class Command(BaseCommand):
    def __init__(self, store):
        super(Command, self).__init__(store)
        self.rx_episode = re.compile(u'(?P<episode_name>S[0-9]{2}E[0-9]{2})')
        self.rx_episode_alt = \
                re.compile(u'(?P<episode_name>[0-9]{1,2}x[0-9]{1,2})')

    def create_parser(self):
        # [-m url|-f file]
        parser = OptionParser()
        parser.add_option("-u", "--force-url", dest="url",
                help="", metavar="URL")
        parser.add_option("-f", "--force-file", dest="file",
                help="", metavar="FILE")

        self.parser = parser
        return parser

    def check_args(self, args):
        (self.options, _) = self.parser.parse_args(args)
        return (getattr(self.options, "url") and not getattr(self.options, "file")) or \
           (getattr(self.options, "file") and not getattr(self.options, "url")) or \
           (not getattr(self.options, "file") and not getattr(self.options, "url"))


    def _save_new_episode(self, show, row):
        """
        Encola en BD un nuevo episodio
        """
        try:
            # SxxEyy numbering scheme
            episode_name = self.rx_episode.findall(row["name"])[0]
        except IndexError:
            try:
                # SxEE numbering scheme
                episode_name = self.rx_episode_alt.findall(row["name"])[0]
                # Normalizes episode numbering to SxxEyy
                episode_name_parts = episode_name.split("x")
                episode_name = "S%02dE%02d" % (int(n) for n in episode_name_parts[:2])
            except IndexError:
                print "Can't find episode number. Aborting."
                return

        episode = show.episodes.find(Episode.name == episode_name).one()
        if not episode:
            episode = Episode()
            episode.name = episode_name
            nospaces_name =  re.sub("\s+", ".", show.name.lstrip().rstrip())
            episode.filename = "%s.%s.avi" % (nospaces_name, episode_name)
            episode.torrent = "%s.%s.torrent" % (nospaces_name, episode_name)
            episode.size = row["size"]
            episode.show = show
            episode.queued = False
            episode.downloaded = False
            episode.url = "\n".join(row["url_torrent"])
            self.store.add(episode)
            self.store.flush()
            self.store.commit()
            return episode
        #elif episode.queued or episode.downloaded:
        else:
            print "Episodio %s:%s already queued or downloaded" % \
                    (show.name, episode.name)
        return

    def run(self):
        print "save_torrents()"

        try:
            scrapper = Scrapper()
            today = scrapper(url=self.options.url, file=self.options.file)
            if not today:
                raise Exception()
        except Exception:
            print "Can't download html. Exiting"
            return

        shows = self.store.find(Show).order_by(Show.name)
        for row in today:
            # Importante: si no pongo list() el cursor queda abierto
            # y se queja de que hay 2 consultas SQL activas
            for show in list(shows):
                if show.match(row["name"]):
                    # Prueba a descargar el fichero
                    if not show.check_size(row["size"]):
                        print u"%s: incorrecto (%3.1f Mb)" % \
                                (row["name"], row["size"])
                    else:
                        episode = self._save_new_episode(show, row)
                        if not episode:
                            break

                        #torrentdl = TorrentManager(row["url_torrent"][0],
                        #        episode.torrent)
                        #if torrentdl():
                        #    episode.queued = True
                        #    self.store.commit()
                        #
                        print "Queued %s %s %s %s %s" % \
                                (show.name, episode.name,
                                 episode.torrent, episode.url,
                                 episode.filename)

