#!/usr/bin/env vpython3
import sys
import json
import logging
from .parse import ClangParse
from .genctypes import CTypes
from .genpybind11 import PyBind11

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG, 
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
)

def main():
    with open(f"{sys.argv[1]}.json", "rt", encoding="utf8") as fp:
        config = json.load(fp)
    cls = ClangParse()
    cls.parse_file(config)
    if cls.errors or cls.fatals:
        return
    cls.visitor()
    if config.get('pybind11'):
        PyBind11(config, cls)
    else:
        CTypes(config, cls)

main()
