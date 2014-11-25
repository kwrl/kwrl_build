from io_utils import process_file, copy_file, zip_files
from styles import lesson_style_debug, note_style
from html_builders import markdown_to_html
import os.path

class Project:
    def __init__(self, filename, number, title, materials, note, embeds):
        self.filename   = filename
        self.number     = number
        self.title      = title
        self.materials  = materials
        self.note       = note
        self.embeds     = embeds

    @staticmethod
    def build_project(term, project, language, theme, output_dir):
        embeds = []
        for file in project.embeds:
            embeds.append(copy_file(file, output_dir))

        input_file = project.filename
        name, ext = os.path.basename(input_file).rsplit(".",1)
        output_files = process_file(input_file, 
            lesson_style_debug, 
            language, 
            theme, 
            output_dir)

        notes = []

        if project.note:
            notes.extend(process_file(project.note, note_style, language, theme, output_dir))
    
        materials = None
        if project.materials:
            zipfilename = "%s_%d-%02.d_%s_%s.zip" % (term.id, term.number, project.number, project.title, language.translate("resources"))
            materials = zip_files(os.path.dirname(input_file), project.materials, output_dir, zipfilename)

        return Project(
            filename = output_files,
            number = project.number,
            title = project.title,
            materials = materials,
            note = notes,
            embeds = embeds,
        )


