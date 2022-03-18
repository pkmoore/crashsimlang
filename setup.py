import os
from setuptools import setup, find_packages


setup(
    name = "port",                
    version = "0.0.1",
    author = "Preston Moore",
    author_email = "pkm266@nyu.edu",
    description = ("Compile and run port automata"),
    url = "https://github.com/pkmoore/crashsimlang",
    install_requires = ["setuptools",
                        "ply",
                        "dill",
                        "lxml",
                        "posix-omni-parser @ git+https://github.com/pkmoore/posix-omni-parser"],
    packages=['port', 'port.compiler', 'port.errors', 'port.transformers'],
    entry_points = {
      "console_scripts": ['port = port.__main__:run_port']                     
    }
)
