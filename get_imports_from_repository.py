# -*- coding: utf-8 -*-
"""

Created on Wed Jul 29 15:08:59 2020

:author: Jared Peacock

:license: MIT

"""

from pathlib import Path

repository_dir = Path(r"c:\Users\peaco\Documents\GitHub\MTarchive\mth5")

imports = []

def get_imports(fn_dir, import_list):
    for fn in fn_dir.iterdir():
        if fn.is_dir():
            import_list = get_imports(fn, import_list)
        elif fn.is_file():
            if fn.suffix == '.py':
                print(fn)
                lines = fn.read_text().split('\n')
                for line in lines:
                    if 'import' in line:
                        if not '>>>' in line:
                            if 'from' in line:
                                line = line.split(' ', 3)
                                for mod in line[-1].split(','):
                                    import_list.append(f"{line[1]}.{mod.strip()}")
                            else:
                                line = line.split()
                                import_list.append(line[1])
                            
                    
    return import_list

imports_list = sorted(list(set(get_imports(repository_dir, []))))
            