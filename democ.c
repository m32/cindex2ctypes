// gcc -fPIC -shared -o democ.so democ.c
#include <stdio.h>
#include "democ.h"

int do_something(
    struct my_point *p1,
    char c1, unsigned char c2,
    short s1, unsigned short s2,
    int i1, unsigned int i2,
    long l1, unsigned long l2,
    float f, double d
) {
    printf("do_something called with: p1=%p c1=%d c2=%d s1=%d s2=%d i1=%d i2=%d l1=%d l2=%d f=%f d=%f\n",
        p1, c1, c2, s1, s2, i1, i2, l1, l2, f, d
    );
    if( p1 != NULL && p1->proc1 != NULL){
        int rc = p1->proc1(0x1234, &i1);
        printf("p1.proc1 result: 0x%x\n", rc);
    }
    int result = c1+c2+s1+s2+i1+i2+l1+l2;
    printf("do_something returning: %d\n", result);
    return result;
}

void voidproc(void){
    printf("voidproc called\n");
}
