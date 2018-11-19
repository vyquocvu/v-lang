#!/bin/bash
rm output*
python main.py
llc -filetype=obj -relocation-model=pic output.ll
gcc output.o -o output
./output