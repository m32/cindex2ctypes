#include "c++.h"
#include <iostream>

int debuglog = 0;
int endvar = 0;
#define ENTERWRAPPER std::cout << "demo::" << __FUNCTION__ << std::endl;
//#define ENTERWRAPPER

ABC::Demo::Demo() {
    ENTERWRAPPER
    this->i1 = 1;
}

ABC::Demo::Demo(int i1, int i2) {
    ENTERWRAPPER
    std::cout
        << "  i1=" << i1 << ", i2=" << i2
        << std::endl;
    this->i1 = 2;
}

ABC::Demo::Demo(char i1) {
    ENTERWRAPPER
    std::cout
        << "  i1=" << i1
        << std::endl;
    this->i1 = 3;
}

int ABC::Demo::cproc(
            char c1, unsigned char c2,
            short s1, unsigned short s2,
            int i1, unsigned int i2,
            long l1, unsigned long l2,
            char *cp1
        ) {
    ENTERWRAPPER
    std::cout
        << "  c1=" << c1 << ", c2=" << c2
        << ", s1=" << s1 << ", s2=" << s2
        << ", i1=" << i1 << ", s2=" << i2
        << ", l1=" << l1 << ", s2=" << l2
        << ", cp=" << cp1
        << std::endl;
    return 1234;
}
