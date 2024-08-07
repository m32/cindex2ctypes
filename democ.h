#define FOO (1 << 2)

#define BAR FOO + 10

typedef int (*cproc)(int a, int b);

union Unia {
    char c1;
    unsigned char c2;
    short s1;
    unsigned short s2;
    int i1;
    unsigned int i2;
    long l1;
    unsigned long l2;
    long long ll1;
    unsigned long long ll2;
    int (*proc)(int x, int *y);
};

typedef struct my_point {
    unsigned long x;
    unsigned long *x1;
    int y;
    int a[BAR + 1];
    int *b[2];
    unsigned long (*proc1)(int x, int *y);
} my_point_t;

enum some_values {
    a_value,
    another_value,
    yet_another_value,
    xx = yet_another_value + 100
};

#define stdcall __attribute__((stdcall))

int do_something(
    struct my_point *p1,
    char c1, unsigned char c2,
    short s1, unsigned short s2,
    int i1, unsigned int i2,
    long l1, unsigned long l2,
    float f1, double d1
);

void voidproc(void);
