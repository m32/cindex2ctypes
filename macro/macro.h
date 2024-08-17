#define X 1
#define Y (1<<1)
#define Z(a) (1<<a)

const int XY = Y<<X;
typedef int xyz[XY];
