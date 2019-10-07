#!/bin/bash
find ../examples/rtl2gds/LIB/lib/tsmc018/OSU_stdcells_tsmc018/ | grep "layout/layout.cdb" | xargs -l ./cdb

