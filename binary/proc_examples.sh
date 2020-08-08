#!/bin/bash
# cdb writes into the output directory
rm -rf output
mkdir output
# Run cdb on the OSU standard cells for tsmc018
find ../examples/rtl2gds/LIB/lib/tsmc018/OSU_stdcells_tsmc018/ | grep "layout/layout.cdb" | xargs --verbose -l ./cdb
