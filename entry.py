#!/usr/bin/python

import interp
import pickle
import marshal
import copyreg
import types
import new

library = "mytech"
cell_name = "nch"
func = "mytech_nch_layout_wrap"
layermap_file = "mytech.layermap"
#File it output of "dbOpenBag(ddGetObj("@lib","@cell"))~>prop~>??"
props_file = "nch_props.il"

#These triplets can be extracted from 'dbDumpPcDefinePcell(dbOpenCellViewByType("@lib" "pch" "layout" "maskLayout") "/tmp/pch.il")'
defaults = """(foo string "0n")
  (bar string "180n")
"""

#Sometimes the code accesses strange variables that aren't even supposed to be defined. 
interp.skill.variables['labelType'] = None

#load defaults into interpreter
interp.load_defaults(defaults)

#codes = ['test.il']
codes = ['cbtools2.il','cbtools.il','cb.il','creategate.il','creatediff.il','nch.il']
#bumping this causes all code to recompile
iversion = 7

#Load props and layermap
interp.init(props_file,layermap_file)
#load the code objects
for c in codes:
  interp.cload(c,iversion)

#This initializes the pcell callback stuff
interp.cdfg_init(library,cell_name)

#Optionally change some parameters through pcell callbacks
interp.pcell_apply('routePolydir','Both')
interp.pcell_apply('w',"500n")
interp.pcell_apply('fingers',"3")
interp.pcell_apply('bodytie_typeR',"Integred")
interp.pcell_apply('routeSD','Both')

#Must be called after pcell updates
interp.apply_params()

try:
   #Run it
   interp.layout(func)
except:
   print interp.skill.variables

   raise
print interp.skill.variables

interp.runtime.write()

#foo = []
#foo[0] = "hello"
#print len(2)

#output = iv.visit(g)
#print output
#if ! Ps4 .new dealloc_return:nt
#print grammar['jump'].parse("jumpr Lr")
#exit(0)

