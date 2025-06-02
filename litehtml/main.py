import demo

demo.debuglog = 1

print("call: demo.Demo()")
cls = demo.Demo()

print("call: demo.Demo(b'1')")
cls = demo.Demo(b'1')

print("call: demo.Demo(1, 2)")
cls = demo.Demo(1, 2)
print('cls.i1=', cls.i1)

if 0:
    res = cls.cproc(
        b'1', b'2',
        1, 2,
        1, 2,
        1, 2,
        b"ala"
    )
    print('cproc=', res)

print('cls.i1=', cls.i1)
