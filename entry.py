#!/usr/bin/python

import interp
import pickle
import marshal
import copyreg
import types
import new

library = "mytech"
layermap_file = "mytech.layermap"

#These triplets can be extracted from 'dbDumpPcDefinePcell(dbOpenCellViewByType("@lib" "pch" "layout" "maskLayout") "/tmp/pch.il")'
nch = {"func"     : "nch_layout",
       "props"    : "nch_props.il", #File it output of "dbOpenBag(ddGetObj("@lib","@cell"))~>prop~>??"
       "cell_name": "nch",
       "defaults" : """
  (foo string "0n")
  (bar string "180n")
"""}




#Sometimes the code accesses strange variables that aren't even supposed to be defined. 
interp.skill.variables['labelType'] = None


#codes = ['test.il']
codes = ['cbtools2.il','cbtools.il','cb.il','creategate.il','creatediff.il','nch.il']
#bumping this causes all code to recompile
iversion = 8

#Load props and layermap
interp.init(layermap_file)
#load the code objects
for c in codes:
  interp.cload(c,iversion)

cell = nch

#load defaults into interpreter
interp.load_defaults(cell['defaults'])

interp.load_props(cell['props'])

#This initializes the pcell callback stuff
interp.cdfg_init(library,cell['cell_name'])

#Optionally change some parameters through pcell callbacks
interp.pcell_apply('w',"500n")
interp.pcell_apply('fingers',"3")

#Must be called after pcell updates
interp.apply_params()

try:
   #Run it
   interp.layout(cell)
except:
   print interp.skill.variables

   raise
print interp.skill.variables

interp.runtime.write()


