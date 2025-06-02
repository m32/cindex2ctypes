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

#include "c++.cpp"

namespace py = pybind11;
using namespace pybind11::literals;

#define ENTERWRAPPER std::cout << "demo::" << __FUNCTION__ << std::endl;
//#define ENTERWRAPPER

PYBIND11_MODULE(demo, m) {
    m.def("_debuglog", [](int value) {
        debuglog = value;
    });

    py::enum_<ABC::Numbers>(m, "Numbers")
        .value("One", ABC::Numbers::One)
        .value("Two", ABC::Numbers::Two)
        .value("Three", ABC::Numbers::Three)

    ;
    py::class_<ABC::Demo>(m, "Demo")
        .def_readwrite("i1", &ABC::Demo::i1)
        .def(py::init<>())
        .def(py::init<char>())
        .def(py::init<int, int>())
        .def("cproc", &ABC::Demo::cproc)
    ;
    m.def("_endvar", [](int value) {
        endvar = value;
    });
}
