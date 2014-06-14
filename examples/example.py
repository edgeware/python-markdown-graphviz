import markdown, sys

extensions = ['ditaa', 'graphviz', 'plantuml']

try:
    extension  = sys.argv[1]
    if extension in extensions:
        fin = open("%s.md" % extension, 'r')
        txt = fin.read()
        fin.close()
        md = markdown.Markdown(extensions=[extension])
        print md.convert(txt)
    else:
        print "Extension(%s) do not exist" % extension
except:
    print "Extensions list:\n\t\t%s" % '\n\t\t'.join(extensions)
    print "%s extension" % sys.argv[0]

