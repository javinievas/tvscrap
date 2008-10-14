# -*- coding: utf-8 -*-
# GNU General Public Licence (GPL)
# 
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA  02111-1307  USA
from base import BaseCommand
from optparse import OptionParser

class Command(BaseCommand):
    def create_parser(self):
        return OptionParser(usage="help")

    def check_args(self, args):
        (options, _) = self.parser.parse_args(args)
        return True

    def run(self):
        print """
tvscrap help
    Show this help
tvscrap register -s <show> -x <rx> [-m xx] [-n xx]
    Register a new show in DB
tvscrap shows
    List of registered shows
tvscrap episodes <show>
    Episode list for a show
tvscrap delete -s <show> [-e <episode>]
    Delete an episode/show from DB
tvscrap pending
    List of pending episodes
tvscrap eztv [-f file|-u url]
    Download torrents from eztv
tvscrap mldonkey [-m host] [-p port] [-u username] [-w password]
    Queue torrents in mldonkey
tvscrap config
    Dump config variables
tvscrap set -n varname -v value
    Set/Update config variable
tvscrap unset -n varname
    Delete config variable
        """