from __future__ import print_function

import sys

import markdown

extensions = ['ditaa', 'graphviz', 'plantuml']

try:
    extension = sys.argv[1]
    if extension in extensions:
        with open("%s.md" % extension) as fin:
            txt = fin.read()
        md = markdown.Markdown(extensions=[extension])
        print(md.convert(txt))
    else:
        print("Extension(%s) do not exist" % extension)
except Exception:
    print("Extensions list:\n\t\t%s" % '\n\t\t'.join(extensions))
    print("%s extension" % sys.argv[0])
