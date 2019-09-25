""" Implements Flag object"""
import yaml
from config import ROOT_DIR


class Flag():
    """
    Class implementing a flag object used in the report generator to build the
    report
    """
    stream = open(str(ROOT_DIR/'src'/'config'/'reco.yaml'))
    reco_dict = yaml.safe_load(stream)

    def __init__(self, id, content=None, location=None):
        self.id = id
        self.content = content
        self.location = location

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
            self.id == other.id and \
            self.content == other.content and \
            self.location == other.location

    def __hash__(self):
        return hash((self.id, self.content, self.location))

    def __repr__(self):
        return str(self.id) +\
               ' | ' + str(self.content) +\
               ' | ' + str(self.location) +\
               '\n'
