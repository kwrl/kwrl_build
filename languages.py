from io_utils import *
import json

class Language:
    def __init__(self, code, name, legal, translations):
        self.code           = code
        self.name           = name
        self.legal          = legal
        self.translations   = translations

    def translate(self, text):
        return self.translations.get(text, text)
    
    @staticmethod
    def parse_language(filename):
        with open(filename) as fh:
            obj = json.load(fh)
    
        return Language(
            code = obj['code'],
            name = obj['name'],
            legal = obj['legal'],
            translations = obj['translations'],
        )

    @staticmethod
    def load_languages(dir):
        languages = {}
        for file in expand_glob(dir,"*.language"): 
            language = Language.parse_language(file)
            languages[language.code] = language
        return languages


