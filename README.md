# Description

The cindex2ctypes is a project to generate python bindings for C code using clang python bindings. 

# Dependencies

**C++**
`sudo apt install -y clang-16 python3-clang-16`

**Python**
`pip install -r requirements.txt`

# Demonstration

Run: `gcc -fPIC -shared -o democ.so democ.c`

Run: `python3 cindex2ctypes.py demo`

The binding code will be available in `demo.py` file.

Run: `python3 demo-main.py`

Output:
```
do_something called with: p1=0x7efd099a2800 c1=49 c2=50 s1=3 s2=4 i1=5 i2=6 l1=7 l2=8 f=9.000000 d=10.000000
cb called with: 0x1234, c_int(5)
p1.proc1 result: 0x1234
do_something returning: 132
do_something result: 132
voidproc called
```
