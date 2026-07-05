#!/usr/bin/env vpython3
import logging

logger = logging.getLogger(__name__)

from .parse import CTVar, CTEnum, CTUnionStruct, CTFunction, CTTypedef, CTClass

def PyBind11(config, parser):
    with open(f"""{config["filename"]}.cpp""", "wt") as fp:
        fp.write(f"""\
#if defined(MS_WIN64)
#define _hypot hypot
#include <cmath>
#else
#include <signal.h>
#define DebugBreak() raise(SIGTRAP)
#endif

#define PYBIND11_DETAILED_ERROR_MESSAGES
#include "pybind11/pybind11.h"
#include "pybind11/stl.h"

#include "{config["parsesrc"]}"

namespace py = pybind11;
using namespace pybind11::literals;

#define ENTERWRAPPER std::cout << "{config["pybindmodule"]}::" << __FUNCTION__ << std::endl;
//#define ENTERWRAPPER

PYBIND11_MODULE({config["pybindmodule"]}, m) {{
""")
        for elem in parser.elements:
            if isinstance(elem, CTEnum):
                elem.write_cpp(fp)
        for elem in parser.elements:
            if isinstance(elem, CTUnionStruct):
                elem.write_cpp(fp)
        for elem in parser.elements:
            if isinstance(elem, CTTypedef):
                elem.write_cpp(fp)
        for elem in parser.elements:
            if isinstance(elem, CTClass):
                elem.write_cpp(fp)
        for elem in parser.elements:
            if isinstance(elem, CTVar):
                elem.write_cpp(fp)
        fp.write(f"""\
}}
""")