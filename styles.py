class Style:
    def __init__(self, name, html_template, tex_template, stylesheets):
        self.name           = name
        self.html_template  = html_template
        self.tex_template   = tex_template
        self.stylesheets    = stylesheets

note_style = index_style = Style(
    name = 'lesson', 
    html_template = "template.html",
    tex_template = None,
    stylesheets = ["/css/main.css", "/css/notes.css"],
)

index_style = Style(
    name = 'lesson', 
    html_template = "template.html",
    tex_template = None,
    stylesheets = ["/css/main.css", "/css/index.css"],
)

index_style_debug = Style(
    name = 'lesson', 
    html_template = "template.html",
    tex_template = None,
    stylesheets = ["/output/css/main.css", "/output/css/index.css"],
)

lesson_style = Style(
    name = 'lesson', 
    html_template = "template.html",
    tex_template = None,
    stylesheets = ["/css/main.css","/css/lesson.css"],
)

lesson_style_debug = Style(
    name = 'lesson',
    html_template = "template.html",
    tex_template = None,
    stylesheets = ["/output/css/main.css", "/output/lesson.css"],
)

lesson_style_relative = Style(
    name = 'lesson',
    html_template = "template.html",
    tex_template = None,
    stylesheets = ["../../../css/main.css", "../../../css/lesson.css"]
)


