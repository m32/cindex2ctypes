typedef struct {
    int x;
    int y;
} S1;
typedef struct {
    unsigned long x;
    int y;
} S2;
typedef struct _X {
    unsigned short et;
    union{
        S1 s1;
        S2 s2;
    }UE;
} IR, *PIR;
