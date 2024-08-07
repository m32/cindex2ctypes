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
