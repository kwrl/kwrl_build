from io_utils import *
from styles import note_style
from print_utils import print_debug, print_error, print_info
from languages import Language
from themes import Theme
from projects import Project
from paths import *
from html_builders import *

import os
import os.path
import sys
import shutil
import collections
import json
import codecs
import tempfile
import string

try:
    import yaml
except ImportError:
    print_error("You need to install pyyaml using pip or easy_install, sorry")
    sys.exit(-10)

# todo : real classes
Term = collections.namedtuple('Term', \
    'id manifest title description language number projects extras')
Extra = collections.namedtuple('Extra', 'name materials note')

# Process files within project and resource containers
def build_extra(term, extra, language, theme, output_dir):
    note = []
    if extra.note:
        note.extend(process_file(extra.note, \
            note_style, \
            language, \
            theme, \
            output_dir))
    materials = None
    if extra.materials:
        zipfilename = "%s_%d_%s_%s.zip" % \
            (term.id, term.number, extra.name, language.translate("resources"))
        materials = zip_files(os.path.dirname(term.manifest), \
            extra.materials, output_dir, zipfilename)
    return Extra(name=extra.name, note=note, materials=materials)

def sort_files(files):
    sort_key = {
        'html':2,
        'pdf':1,
    }
    return sorted(files, key=lambda x: sort_key.get(x.format, 0), reverse=True)

#Find manifests and add all build languages
def get_termlangs(repositories, all_languages):
    print_info("Searching for manifests ..")
    termlangs = {}
    for m in find_files(repositories, ".manifest"):
        print_info("Found Manifest:" +str(m))
        try:
            term = parse_manifest(m)
            if term.language not in termlangs:
                termlangs[term.language] = []
            termlangs[term.language].append(term)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print_error("Failed" + e)
    return termlangs

# The all singing all dancing build function of doing everything.
def build(repositories, theme, all_languages, output_dir):
    termlangs = get_termlangs(repositories, all_languages)

    print_info("Copying assets")
    copydir(html_assets, output_dir)
    css_dir = os.path.join(output_dir, "css")
    makedirs(css_dir)
    make_css(css_assets, theme, css_dir)

    languages = {}
    project_count = {}

    for language_code, terms in termlangs.items():
        if language_code not in all_languages:
            all_languages[language_code] = Language(
                code=language_code,
                name=language_code,
                legal={},
                translations={}
            )
        language = all_languages[language_code]
        print_info("Language "+language.name)
        out_terms = []
        count = 0
        lang_dir = os.path.join(output_dir, language.code)

        for term in terms:
            term_dir = os.path.join(lang_dir, "%s.%d"%(term.id, term.number))
            makedirs(term_dir)
            print_info("Building Term:\t\t" + str(term.title))
            projects = []

            for p in term.projects:
                built_project = Project.build_from_resource(p, \
                    term, \
                    term_dir, \
                    language, \
                    theme)
                if built_project:
                    count += 1
                    projects.append(built_project)
                else:
                    continue

            extras = []
            for r in term.extras:
                extras.append(build_extra(term, r, language, theme, term_dir))

            term = Term(
                id=term.id,
                manifest=term.manifest,
                number=term.number, language=term.language,
                title=term.title, description=term.description,
                projects=projects,
                extras=extras,
            )

            out_terms.append(make_term_index(term, language, theme, term_dir))

            print_info("Term built!")

        print_info("Building " + language.name +" index")

        languages[language_code] = \
            make_lang_index(language, out_terms, theme, lang_dir)
        project_count[language_code] = count

    print_info("Building " + theme.name + " index: " + output_dir)

    sorted_languages = []
    for lang in sorted(project_count.keys(), \
            key=lambda x: project_count[x], reverse=True):
        sorted_languages.append((all_languages[lang], languages[lang]))

    make_index(sorted_languages, \
        all_languages[theme.language], \
        theme, \
        output_dir)
    print_info("Complete")

def parse_manifest(filename):
    fh = codecs.open(filename, "r", "utf-8").read()
    json_manifest = json.loads(fh)
    base_dir = os.path.join(os.path.dirname(filename))
    projects = []
    for p in json_manifest['projects']:
        filename = expand_glob(base_dir, p['filename'], one_file=True)
        materials = expand_glob(base_dir, p.get('materials', []))
        embeds = expand_glob(base_dir, p.get('embeds', []))

        if 'note' in p:
            note = expand_glob(base_dir, p['note'], one_file=True)
        else:
            note = None
 
        project = Project(
            filename=filename,
            number=p['number'],
            title=p.get('title', None),
            materials=materials,
            note=note,
            embeds=embeds,
        )
        projects.append(project)

    extras = []
    for s in json_manifest.get('extras', ()):
        if 'note' in s:
            note = expand_glob(base_dir, s['note'], one_file=True)
        else:
            note = None
        materials = expand_glob(base_dir, s.get('materials', ()))
 
        extras.append(Extra(
            name=s['name'],
            note=note,
            materials=materials,
        ))

    m = Term(
        id=json_manifest['id'],
        title=json_manifest['title'],
        manifest=filename,
        description=json_manifest['description'],
        language=json_manifest['language'],
        number=int(json_manifest['number']),
        projects=projects,
        extras=extras,
    )
    return m

def make_css(stylesheet_dir, theme, output_dir):
    for asset in os.listdir(stylesheet_dir):
        if not asset.startswith('.'):
            src = os.path.join(stylesheet_dir, asset)
            dst = os.path.join(output_dir, asset)
            if os.path.exists(dst):
                if os.path.isdir(dst):
                    shutil.rmtree(dst)
                    makedirs(dst)
                else:
                    os.remove(dst)

            if os.path.isdir(src):
                make_css(src, theme, dst)
            else:
                if asset.endswith('.css'):
                    with codecs.open(src,"r", "utf-8") as src_fh, \
                            codecs.open(dst, "w", "utf-8") as dst_fh:
                        template = string.Template(src_fh.read())
                        dst_fh.write(template.substitute(theme.css_variables))
                else:
                    shutil.copy(src, output_dir)

THEMES = Theme.load_themes(theme_base)
LANGUAGES = Language.load_languages(language_base)

if __name__ == '__main__':
    args = sys.argv[1::]
    if len(args) < 3:
        print_error("usage: %s <region> <input repository directories> <output directory>")
        sys.exit(-1)
    theme = THEMES[args[0]]
    languages = LANGUAGES
    args = [os.path.abspath(a) for a in args[1:]]
    repositories, output_dir = args[:-1], args[-1]
    build(repositories, theme, languages, output_dir)
    sys.exit(0)

