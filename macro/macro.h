#include <stdio.h>

#define A0 1L
#define A1 1U
#define A2 1UL
#define A3
#define A4 NULL

#define X 1
#define Y (1L<<1)
#define Z(a) (1<<a)

const int XY = Y<<X;
typedef int xyz0[XY];
typedef int xyz1[Y<<X];
