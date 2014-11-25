from io_utils import *
import json

class Theme:
    def __init__(self, *args, **kwargs):
        self.id             = kwargs.get("id")
        self.name           = kwargs.get("name")
        self.language       = kwargs.get("language")
        self.stylesheets    = kwargs.get("stylesheets")
        self.legal          = kwargs.get("legal")
        self.logo           = kwargs.get("logo")
        self.css_variables  = kwargs.get("css_variables")

    @staticmethod
    def parse_theme(filename):
        with open(filename) as fh:
            obj = json.load(fh)
    
        return Theme(
            id = obj['id'],
            name = obj['name'],
            language = obj['language'],
            stylesheets = obj['stylesheets'],
            legal = obj['legal'],
            logo = obj['logo'],
            css_variables = obj['css_variables'],
        )
    @staticmethod
    def load_themes(dir):
        themes = {}
        for file in expand_glob(dir,"*.theme"): 
            theme = Theme.parse_theme(file)
            themes[theme.id] = theme
        return themes


