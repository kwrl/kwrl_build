from io_utils import process_file, copy_file, zip_files, makedirs, expand_glob
from print_utils import print_info, print_error
from styles import lesson_style_debug, note_style
from html_builders import markdown_to_html
import os.path
import codecs
import yaml

class Project:
    def __init__(self, filename, number, title, materials, note, embeds):
        self.filename   = filename
        self.number     = number
        self.title      = title
        self.materials  = materials
        self.note       = note
        self.embeds     = embeds

    @staticmethod
    def build_from_resource(resource, term, term_dir, language, theme):
        try: 
            print_info("Project building..\t" + str(resource.filename))
        except:
            print_error("Project failed due to filename encoding: " + str(resource.filename))
            return None

        project     = Project.parse_project_meta(resource)
        project_dir = os.path.join(term_dir,"%.02d"%(project.number))
        makedirs(project_dir)

        try:
            built_project = Project.build_project(term, project, language, theme, project_dir)
        except:
            print_error("Project failed while building: " + str(resource.filename))
            return None

        print_info("Project done!\t\t" + str(resource.filename))
        return built_project

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

    def parse_project_meta(p):
        if not p.filename.endswith('md'):
            return p

        with codecs.open(p.filename,"r", "utf-8") as fh:
            in_header = False
            header_lines = []
            for line in fh.readlines():
                l = line.strip()
                if l == "---":
                    in_header = True
                elif l == "...":
                    in_header = False
                elif in_header:
                    header_lines.append(line)
        header = yaml.safe_load("".join(header_lines))

        if header:
            title   = header.get('title', p.title)
            number  = header.get('number', p.number)
            title   = header.get('title', p.title)

            raw_note = header.get('note', None)
            if raw_note:
                base_dir = os.path.dirname(p.filename)
                note = expand_glob(base_dir, raw_note, one_file=True)
            else:
                note = p.note

            raw_materials = header.get('materials', ())
            if raw_materials:
                base_dir = os.path.dirname(p.filename)
                materials = expand_glob(base_dir, raw_materials)
                materials.extend(p.materials)
            else:
                materials = p.materials

            raw_embeds = header.get('embeds', ())
            if raw_embeds:
                base_dir = os.path.dirname(p.filename)
                embeds = expand_glob(base_dir, raw_embeds)
                embeds.extend(p.embeds)
            else:
                embeds = p.embeds

            return Project(
                filename = p.filename,
                number = number,
                title = title,
                materials = materials,
                note = note,
                embeds = embeds,
            )
        else:
            return p
