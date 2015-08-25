"""
### Markdown-Python-Graphviz

This module is an extention to [Python-Markdown][pymd] which makes it
possible to embed [Graphviz][gv] syntax into Markdown documents.

### Requirements

Using this module requires:
   * Python-Markdown
   * Graphviz (particularly ``dot``)

### Syntax

Wrap Graphviz definitions within a dot/neato/dotty/lefty tag.

An example document:

    This is some text above a graph.

    <dot>
    digraph a {
        nodesep=1.0;
        rankdir=LR;
        a -> b -> c ->d;
    }
    </dot>

    Some other text between two graphs.

    <neato>
    some graph in neato...
    </neato>

    This is also some text below a graph.

Note that the opening and closing tags should come at the beginning of
their lines and should be immediately followed by a newline.

### Usage

    import markdown
    md = markdown.Markdown(
            extensions=['graphviz'],
            extension_configs={'graphviz' : {'DOT','/usr/bin/dot'}}
    )
    return md.convert(some_text)


[pymd]: http://www.freewisdom.org/projects/python-markdown/ "Python-Markdown"
[gv]: http://www.graphviz.org/ "Graphviz"

"""
from os.path import exists
import re
import subprocess

import crcmod.predefined
import markdown
import markdown.preprocessors


class GraphvizExtension(markdown.Extension):
    def __init__(self, configs):
        self.config = {'BINARY_PATH': "", 'WRITE_IMGS_DIR': "",
                       "BASE_IMG_LINK_DIR": "", "FORMAT": "png"}
        for key, value in configs:
            self.config[key] = value

    def reset(self):
        pass

    def extendMarkdown(self, md, md_globals):
        """Add GraphvizExtension to the Markdown instance."""
        md.registerExtension(self)
        self.parser = md.parser
        md.preprocessors.add('graphviz', GraphvizPreprocessor(self), '_begin')


class GraphvizPreprocessor(markdown.preprocessors.Preprocessor):
    """Find all graphviz blocks, generate images and inject image link to
    generated images.
    """

    def __init__(self, graphviz):
        self.formatters = ["dot", "neato", "lefty", "dotty"]
        self.graphviz = graphviz
        self.start_re = re.compile(r'^<(%s)>' % '|'.join(self.formatters))
        self.end_re = re.compile(r'^</(%s)>' % '|'.join(self.formatters))
        self.crc64 = lambda x: crcmod.predefined.mkCrcFun('crc-64')(x)

    def run(self, lines):
        new_lines = []
        block = []
        in_block = None
        for line in lines:
            start_tag = self.start_re.match(line)
            end_tag = self.end_re.match(line)
            if start_tag:
                assert(block == [])
                in_block = start_tag.group(1)
            elif end_tag:
                new_lines.append(self.graph(in_block, block))
                block = []
                in_block = None
            elif in_block in self.formatters:
                block.append(line)
            else:
                new_lines.append(line)
        assert(block == [])
        return new_lines

    def graph(self, type, lines):
        """Generates a graph from lines and returns a string containing n image
        link to created graph."""

        code = "\n".join(lines)
        name = self.crc64(code)

        assert(type in self.formatters)
        filepath = "%s%s.%s" % (self.graphviz.config["WRITE_IMGS_DIR"],
                                name, self.graphviz.config["FORMAT"])
        if not exists(filepath):
            cmd = "%s%s -T%s" % (self.graphviz.config["BINARY_PATH"],
                                 type,
                                 self.graphviz.config["FORMAT"])
            p = subprocess.Popen(cmd, shell=True,
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE, close_fds=True)
            p.stdin.write(code)
            p.stdin.close()
            p.wait()

            with open(filepath, 'w') as fout:
                fout.write(p.stdout.read())

        output_path = "%s%s.%s" % (self.graphviz.config["BASE_IMG_LINK_DIR"],
                                   name,
                                   self.graphviz.config["FORMAT"])
        return "![Graphviz chart %s](%s)" % (name, output_path)


def makeExtension(configs=None):
    return GraphvizExtension(configs=configs)
