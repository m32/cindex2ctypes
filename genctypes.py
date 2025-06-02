#!/usr/bin/env vpython3
import logging

logger = logging.getLogger(__name__)

from .parse import CTEnum, CTUnionStruct, CTFunction, CTTypedef, CTClass

def CTypes(config, parser):
    with open(f"{config['filename']}.py", "wt") as fp:
        fp.write("""\
from ctypes import (
    CDLL, CFUNCTYPE, POINTER,
    Union, Structure, sizeof,
    c_size_t, c_int,
    c_int8, c_uint8,
    c_int16, c_uint16,
    c_int32, c_uint32,
    c_int64, c_uint64,
    c_int64, c_uint64,
    c_float, c_double
)

int8_t = c_int8
int16_t = c_int16
int32_t = c_int32
int64_t = c_int64
uint8_t = c_uint8
uint16_t = c_uint16
uint32_t = c_uint32
uint64_t = c_uint64

size_t = c_size_t
""")
        fp.write("\n")
        for name, value in parser.macros:
            fp.write(f"{value}\n")
        fp.write("\n")

        noenumclass = config.get("noenumclass", False)
        if noenumclass:
            for elem in parser.elements:
                if isinstance(elem, CTEnum):
                    fp.write(f"""\
{elem.name} = c_int32
""")
            if parser.elements:
                fp.write("""
if 1:
""")
            for elem in parser.elements:
                if isinstance(elem, CTEnum):
                    fp.write(f"""\
    # {elem.name}
""")
                    elem.write_py_children(fp)
        else:
            for elem in parser.elements:
                if isinstance(elem, CTEnum):
                    elem.write(fp)

        for elem in parser.elements:
            if isinstance(elem, CTUnionStruct):
                elem.write_py(fp)
            elif isinstance(elem, CTTypedef):
                elem.write_py(fp)
            elif isinstance(elem, CTClass):
                elem.write_py(fp)

        fp.write(f"""
class {config['classname']}:
    def __init__(self, path):
        self.hdll = CDLL(path)
""")
        functions_decorated = config.get("functions_decorated", False)
        if functions_decorated:
            fp.write("""
        def cdecl(restype, *argtypes):
            def decorate(func):
                api = CFUNCTYPE(restype, *argtypes)((func.__name__, self.hdll))
                func._api_ = api
                return func
            return decorate
""")
            for elem in parser.elements:
                if isinstance(elem, CTFunction):
                    elem.decorated(fp)
            fp.write("\n")
            for elem in parser.elements:
                if isinstance(elem, CTFunction):
                    elem.decorated_def(fp)
        else:
            for elem in parser.elements:
                if isinstance(elem, CTFunction):
                    elem.write_py(fp)
