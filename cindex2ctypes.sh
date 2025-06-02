#!/bin/bash
PYTHONPATH=$(dirname $(dirname $(readlink -f $0)))
vpython3 -m cindex2ctypes $*
