from styles import index_style_debug
from paths import *
import xml.etree.ElementTree as ET
import subprocess
import os

def markdown_to_html(markdown_file, style, language, theme, output_file):
    commands = (
        "-f", "markdown_github+header_attributes+yaml_metadata_block+inline_code_attributes",
    )
    pandoc_html(markdown_file, style, language, theme, {}, commands, output_file)

def pandoc_html(input_file, style, language, theme, variables, commands, output_file):
    legal = language.legal.get(theme.id, theme.legal)
    cmd = [
        "pandoc",
        input_file, 
        "-o", output_file,
        "-t", "html5",
        "-s",  # smart quotes
        "--highlight-style", "pygments",
        "--section-divs",
        "--template=%s"%os.path.join(template_base, style.html_template), 
        "--filter", scratchblocks_filter,
        "-M", "legal=%s"%legal,
        "-M", "organization=%s"%theme.name,
        "-M", "logo=%s"%theme.logo,
    ]
    for stylesheet in style.stylesheets:
        cmd.extend(("-c", stylesheet,))
    for stylesheet in theme.stylesheets:
        cmd.extend(("-c", stylesheet,))
    for k,v in variables.items(): 
        cmd.extend(("-M", "%s=%s"%(k,v)))
    
    working_dir = os.path.dirname(output_file)
    subprocess.check_call(cmd, cwd=working_dir)

def sort_files(files):
    sort_key = {
        'html':2,
        'pdf':1,
    }
    return sorted(files, key=lambda x:sort_key.get(x.format,0), reverse=True)

def make_html(variables, html, style, language, theme, output_file):
    variables = dict(variables)
    variables['body'] = ET.tostring(html, encoding='utf-8', method='html')
    commands = (
        "-f", "html",
        "-R",
    )
    input_file = '/dev/null'
    pandoc_html(input_file, style, language, theme, variables, commands, output_file)

def make_term_index(term, language, theme, output_dir):
    output_file = os.path.join(output_dir, "index.html")
    title = term.title
    root = ET.Element('body')
    if term.description:
        section = ET.SubElement(root,'section', {'class':'description'})
        p = ET.SubElement(section, 'p')
        p.text = term.description

    section = ET.SubElement(root,'section', {'class':'projects'})
    h1 = ET.SubElement(section,'h1')
    h1.text = language.translate("Projects")
    ol = ET.SubElement(root, 'ol', {'class': 'projectlist'})
    
    for project in sorted(term.projects, key=lambda x:x.number):
        li = ET.SubElement(ol, 'li')
        ul = ET.SubElement(li, 'ul', {'class': 'projectfiles'})

        files = sort_files(project.filename)
        first, others = files[0], files[1:]

        url = os.path.relpath(first.filename, output_dir)

        a_li = ET.SubElement(ul, 'li', {'class':'worksheet'})
        a = ET.SubElement(a_li, 'a', {'href': url})
        a.text = project.title or url

        for file in others:
            url = os.path.relpath(file.filename, output_dir)
            a_li = ET.SubElement(ul, 'li', {'class':'alternate'})
            a = ET.SubElement(a_li, 'a', {'href': url})
            a.text = file.format
            if file.format == 'pdf':
                a.text = (project.title or url) + ' (pdf)'
            
        for file in sort_files(project.note):
            url = os.path.relpath(file.filename, output_dir)
            a_li = ET.SubElement(ul, 'li', {'class':'notes'})
            a = ET.SubElement(a_li, 'a', {'href': url})
            if file.format != 'html':
                a.text = "%s (%s)"%(language.translate("Notes"),file.format)
            else:
                a.text = language.translate("Notes")

        if project.materials:
            file = project.materials
            url = os.path.relpath(file.filename, output_dir)
            a_li = ET.SubElement(ul, 'li', {'class':'materials'})
            a = ET.SubElement(a_li, 'a', {'href': url, 'class':'materials'})
            a.text = "%s (%s)"%(language.translate("Materials"),file.format)

    section = ET.SubElement(root, 'section', {'class':'extras'})
    h1 = ET.SubElement(section, 'h1')
    h1.text = language.translate('Extras')

    ol = ET.SubElement(root, 'ol', {'class':'extralist'})
    for extra in term.extras:
        if extra.note:
            file = sort_files(extra.note)[0]
            # todo: handle multiple formats
            url = os.path.relpath(file.filename, output_dir)
            li = ET.SubElement(ol, 'li', {'class':'extranote'})
            a = ET.SubElement(li, 'a', {'href': url})
            a.text = extra.name
        
        if extra.materials: 
            filename = extra.materials
            url = os.path.relpath(filename, output_dir)
            li = ET.SubElement(ol, 'li', {'class':'extramaterial'})
            a = ET.SubElement(li, 'a', {'href': url})
            a.text = filename

    make_html({'title':title, 'level':"T%d"%term.number}, root, index_style_debug, language, theme, output_file)
    return output_file, term

def make_lang_index(language, terms, theme, output_dir):
    output_file = os.path.join(output_dir, "index.html")
    root = ET.Element('section', {'class':'termlist'})
    h1 = ET.SubElement(root, 'h1')
    h1.text = language.translate("Terms")
    ol = ET.SubElement(root, 'ol')
    for term_index, term in sorted(terms, key=lambda x:x[1].number):
        url = os.path.relpath(term_index, output_dir)

        li = ET.SubElement(ol, 'li', {'class':'term'})
        a = ET.SubElement(li, 'a', {'href': url})
        a.text = term.title or url

    make_html({'title':language.name}, root, index_style_debug, language, theme, output_file)
    return output_file

def make_index(languages, language, theme, output_dir):
    output_file = os.path.join(output_dir, "index.html")
    title = theme.name

    root = ET.Element('section')
    h1 = ET.SubElement(root, 'h1')
    h1.text = language.translate("Languages")
    ol = ET.SubElement(root, 'ol', {'class':'langs'})

    for lang, filename in languages:
        url = os.path.relpath(filename, output_dir)

        li = ET.SubElement(ol, 'li', {'class':'lang'})
        a = ET.SubElement(li, 'a', {'href': url})
        a.text = lang.name
    make_html({'title':title}, root, index_style_debug, language, theme, output_file)


