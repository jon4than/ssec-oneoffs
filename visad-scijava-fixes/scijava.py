import fnmatch
import logging
import os

# order is important!
old_packages = set([
    ('com.sun.j3d.utils.scenegraph.io.state.com.sun.j3d', 'org.scijava.java3d.utils.scenegraph.io.state.org.scijava.java3d'),
    ('com.sun.j3d.utils.scenegraph.io.state.javax.media.j3d', 'org.scijava.java3d.utils.scenegraph.io.state.org.scijava.java3d'),
    ('javax.media.j3d', 'org.scijava.java3d'),
    ('com.sun.j3d', 'org.scijava.java3d'),
    ('javax.vecmath', 'org.scijava.vecmath')
])

VISAD_SRC = ''

OLD_PREFIX = ''

NEW_PREFIX = ''

def find_files(path, mask):
    for path, dir_list, file_list in os.walk(path):
        for name in fnmatch.filter(file_list, mask):
            yield os.path.join(path, name)

def open_files(files, mode='r'):
    for f in files:
        yield open(f, mode)

def read_files(handles):
    for handle in handles:
        yield handle.name, (line for line in handle)

def fix_imports(pairs):
    for fname, line_gen in pairs:
        yield fname, fix_import(line_gen)

def fix_import(gen):
    for line in gen:
        for pkg in old_packages:
            if pkg[0] in line:
                line = line.replace(pkg[0], pkg[1])
        yield line

def fix_paths(lines, old_portion, new_portion):
    for file_path, handle in lines:
        file_dir, file_name = os.path.split(file_path)
        file_dir = file_dir.replace(old_portion, new_portion)
        os.makedirs(file_dir, exist_ok=True)
        yield os.path.join(file_dir, file_name), handle

def fix_everything(current_state, old_portion, new_portion):
    for old_path, old_contents in current_state:
        file_dir, file_name = os.path.split(old_path)
        file_dir = file_dir.replace(old_portion, new_portion)
        os.makedirs(file_dir, exist_ok=True)
        new_path = os.path.join(file_dir, file_name)
        yield new_path, fix_import(old_contents)

def save_files(corrected_output):
    for corrected_file, corrected_lines in corrected_output:
        with open(corrected_file, 'w') as handle:
            handle.writelines(corrected_lines)

def scijava_imports(visad_dir):
    java_files      = find_files(visad_dir, '*.java')
    file_handles    = open_files(java_files)
    current_lines   = read_files(file_handles)
    output_files    = fix_paths(current_lines, OLD_PREFIX, NEW_PREFIX)
    corrected_lines = fix_imports(output_files)
    
    save_files(corrected_lines)

def scijava_imports2(visad_dir):
    java_files       = find_files(visad_dir, '*.java')
    file_handles     = open_files(java_files)
    current_lines    = read_files(file_handles)
    corrected_output = fix_everything(current_lines, OLD_PREFIX, NEW_PREFIX)
    
    save_files(corrected_output)

def main():
    # scijava_imports('/Users/jbeavers/work/idea/visad/core')
    scijava_imports2(VISAD_SRC)

if __name__ == '__main__':
    logging.basicConfig(format='! %(asctime)s - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %I:%M:%S%p', level=logging.DEBUG)
    if not all([VISAD_SRC, OLD_PREFIX, NEW_PREFIX]):
        logging.error('paths must be set prior to running! TODO: use env vars')
    main()
