# -*- coding: utf-8 -*-
from db import Config

class BaseCommand(object):
    def __init__(self, store):
        self.store = store
        self.parser = self.create_parser()
        self.options = {}

    def create_parser(self):
        raise NotImplementedError #pass

    def check_args(self, args):
        return False

    def show_help(self):
        print self.parser.format_help()

    def run(self):
        raise NotImplementedError #pass

    def get_config(self, varname):
        var = self.store.find(Config, Config.varname == unicode(varname)).one()
        if var:
            return var.value
        else:
            return ""

    def _best_value(self, opt, config_var, default):
        if opt:
            return opt

        tmp = self.get_config(config_var)
        if tmp:
            return tmp

        return default

