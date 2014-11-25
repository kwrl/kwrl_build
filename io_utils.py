from html_builders import markdown_to_html

import os
import re
import glob
import shutil
import subprocess

class Resource:
    def __init__(self, format, filename):
        self.format = format
        self.filename = filename

def copy_file(input_file, output_dir):
    name, ext = os.path.basename(input_file).rsplit(".",1)
    output_file = os.path.join(output_dir, os.path.basename(input_file))
    shutil.copy(input_file, output_file)
    return output_file
"""
def find_files(dir, extension):
    manifests = []
    def visit(m, dirname, names):
        for n in names:
            if n.endswith(extension):
                m.append(os.path.join(dirname, n))
    for d in dir:
        os.walk(d, visit, manifests)
    return manifests
"""
def find_files(dir, extension):
    manifests = []
    for d in dir:
        for root, dirs, files in os.walk(d):
            for file in files:
                if file.endswith(extension):
                    manifests.append(os.path.join(root, file))
    return manifests

def expand_glob(base_dir, paths, one_file=False):
    if one_file:
        output = glob.glob(os.path.join(base_dir, paths))
        if len(output) != 1:
            import ipdb
            ipdb.set_trace()
            raise AssertionError("Bad things")
        return output[0]
    else:
        output = []
        if not hasattr(paths, '__iter__'):
            paths = (paths,)
        for p in paths:
            try:
                output.extend(glob.glob(os.path.join(base_dir, p)))
            except:
                import ipdb
                ipdb.set_trace()
        output = [x for x in output if not x.endswith("/.")]
        return output
    
def makedirs(path, clear=False):
    if clear and os.path.exists(path):
        shutil.rmtree(path)
    if not os.path.exists(path):
        os.makedirs(path)

def zip_files(relative_dir, source_files, output_dir, output_file):
    if source_files:
        output_file = os.path.join(output_dir, safe_filename(output_file))
        cmd = [
            'zip'
        ]
        if os.path.exists(output_file):
            os.remove(output_file)

        cmd.append(output_file)
        for file in source_files:
            cmd.append(os.path.relpath(file, relative_dir))
        
        ret = subprocess.call(cmd, cwd=relative_dir)
        if ret != 0 and ret != 12: # 12 means zip did nothing
            raise StandardError('zip failure %d'%ret)
        return Resource(format="zip", filename=output_file)
    else:
        return None

def safe_filename(filename):
    banned_chars=re.compile(r'[\\/?|;:!#@$%^&*<>, ]+')
    return banned_chars.sub("_", filename)

def copydir(assets, output_dir):
    for src in assets:
        asset = os.path.basename(src)
        if not asset.startswith('.'):
            dst = os.path.join(output_dir, asset)
            if os.path.exists(dst):
                if os.path.isdir(dst):
                    shutil.rmtree(dst)
                else:
                    os.remove(dst)
                    
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy(src, output_dir)

def process_file(input_file, style, language, theme, output_dir):
    output = []
    name, ext = os.path.basename(input_file).rsplit(".",1)
    if ext == "md":
        output_file = os.path.join(output_dir, "%s.html"%name)
        markdown_to_html(input_file, style, language, theme, output_file)
        output.append(Resource(filename=output_file, format="html"))
    else:
        output_file = os.path.join(output_dir, os.path.basename(input_file))
        shutil.copy(input_file, output_file)
        output.append(Resource(filename=output_file, format=ext))
    return output 
