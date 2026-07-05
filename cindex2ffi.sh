#!/bin/bash
PYTHONPATH=$(dirname $(dirname $(readlink -f $0)))
vpython3 -m cindex2ffi cfg >x-out-1 2>x-out-2
