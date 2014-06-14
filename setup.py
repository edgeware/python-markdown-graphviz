from distutils.core import setup

setup(
    name='python-markdown-graphviz',
    version='0.2.1',
    url='https://github.com/edgeware/python-markdown-graphviz',
    py_modules=['mdx_graphviz', 'mdx_ditaa', 'mdx_plantuml', 'mdx_boldcode'],
    install_requires=[
            'Markdown>=2.3.1',
            'crcmod>=1.7',
    ]
)
