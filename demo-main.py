from ctypes import byref
import demo

def cb(a, b):
    print(f'cb called with: 0x{a:x}, {b.contents}')
    return 0x1234

cls = demo.Demo("./democ.so")
pt = demo.my_point()
pt.x = 0x123456789abcef0
pt.x1 = None
pt.y = 0x12345678
pt.proc1 = demo.my_point._fields_[-1][1](cb)
rc = cls.do_something(
    byref(pt),
    ord('1'), ord('2'),
    3, 4,
    5, 6,
    7, 8,
    9, 10
)
print('do_something result:', rc)
cls.voidproc()
