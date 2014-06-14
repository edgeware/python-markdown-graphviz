"""
### Markdown-Python-PlantUML

Based on mdx_graphviz.py, see it for details.

"""
import markdown
import markdown.preprocessors
import crcmod.predefined
import os, re
import shutil
import subprocess
import tempfile


class PlantUMLExtension(markdown.Extension):
    def __init__(self, configs):
        self.config = {'BINARY_PATH': "", 'WRITE_IMGS_DIR': "",
                       "BASE_IMG_LINK_DIR": "", "ARGUMENTS": ""}
        for key, value in configs:
            self.config[key] = value

    def reset(self):
        pass

    def extendMarkdown(self, md, md_globals):
        "Add PlantUMLExtension to the Markdown instance."
        md.registerExtension(self)
        self.parser = md.parser
        md.preprocessors.add('plantuml', PlantUMLPreprocessor(self), '_begin')


class PlantUMLPreprocessor(markdown.preprocessors.Preprocessor):
    """Find all plantuml blocks, generate images and inject image link to
    generated images.
    """

    def __init__(self, plantuml):
        self.formatters = ["plantuml"]
        self.plantuml = plantuml
        self.start_re = re.compile(r'^<(%s)>' % '|'.join(self.formatters))
        self.end_re   = re.compile(r'^</(%s)>' % '|'.join(self.formatters))
        self.crc64    = lambda x: crcmod.predefined.mkCrcFun('crc-64')(x)

    def run(self, lines):
        new_lines = []
        block = []
        in_block = None
        for line in lines:
            start_tag = self.start_re.match(line)
            end_tag   = self.end_re.match(line)
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

    def graph(self, kind, lines):
        """Generates a graph from lines and returns a string containing an
        image link to created graph.
        """

        code = "\n".join(lines)
        name = self.crc64(code)

        assert(kind in self.formatters)
        filepath = "%s%s.png" % (self.plantuml.config["WRITE_IMGS_DIR"], name)
        if not os.path.exists(filepath):
            tmp = tempfile.NamedTemporaryFile()
            tmp.write("@startuml\n" + code + "\n@enduml\n")
            tmp.flush()
            cmd = "%s %s %s" % (
                os.path.join(self.plantuml.config["BINARY_PATH"], kind),
                self.plantuml.config["ARGUMENTS"], tmp.name)
            p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE, close_fds=True)
            p.wait()
            shutil.copyfile(tmp.name, filepath)

        output_path = "%s%s.png" % (self.plantuml.config["BASE_IMG_LINK_DIR"], name)
        return "![PlantUML chart %s](%s)" % (name, output_path)


def makeExtension(configs=None):
    return PlantUMLExtension(configs=configs)
