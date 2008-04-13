# -*- coding: utf-8 -*-
"""
db.py

Modelos de la BD de series
"""
import sys
import os
import re
import storm.locals as st

class TVConfigError(Exception):
    """
    Excepcion de configuracion incorrecta de la
    BD de series
    """
    pass

class Show(object):
    """ Modelo para almacenar una Serie """
    __storm_table__ = 'shows'
    id = st.Int(primary=True)
    name = st.Unicode()
    regexp_filter = st.Unicode()
    min_size = st.Float()
    max_size = st.Float()

    def __unicode__(self):
        return self.name

    def match(self, candidate):
        """ Comprueba si el parametro cumple la expresion regular """
        return re.compile(self.regexp_filter).match(candidate)

    def check_size(self, size):
        """ Comprueba si el tamaño está dentro de los límites """
        return (self.max_size == 0.0 or size <= self.max_size) and \
                (self.min_size == 0.0 or size >= self.min_size)

class Episode(object):
    """ Modelo para almacenar un Episodio de una serie """
    __storm_table__ = 'episodes'
    id = st.Int(primary=True)
    show_id = st.Int()
    show = st.Reference(show_id, Show.id)
    name = st.Unicode() # SxxEyy
    filename = st.Unicode()
    torrent = st.Unicode()
    size = st.Float()
    queued = st.Bool()
    downloaded = st.Bool()

    def __unicode__(self):
        return self.name

Show.episodes = st.ReferenceSet(Show.id, Episode.show_id)

class Config(object):
    """ Modelo para manejar configuracion del programa """
    __storm_table__ = 'config'
    id = st.Int(primary=True)
    varname = st.Unicode()
    value = st.Unicode()

    def __unicode__(self):
        return self.varname

def config_program_folder():
    """
    Fabrica el nombre de la BD de series a partir
    del directorio HOME en Win32 y POSIX
    """
    if sys.platform == 'win32':
        homedir = "%s%s" % \
                (os.environ.get("HOMEDRIVE"), os.environ.get("HOMEPATH"))
    else:
        homedir = os.environ.get("HOME")

    if not homedir:
        configdir = '.'
    else:
        configdir = os.path.join(homedir, ".tvscrap")

    if not os.path.exists(configdir):
        os.mkdir(configdir)
    else:
        if not os.path.isdir(configdir):
            raise TVConfigError()

    return configdir

def get_db_filename():
    """ Devuelve el nombre de la BD de series """
    homedir = config_program_folder()
    return os.path.join(homedir, "tvscrap.db")

def connect_db():
    """ Conecta con la BD de series """
    dsn = "sqlite:%s" % get_db_filename()
    return st.create_database(dsn)

