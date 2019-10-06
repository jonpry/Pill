#!/usr/bin/python3

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
       "props"    : "nch_props.il", #File is output of "dbOpenBag(ddGetObj("@lib","@cell"))~>prop~>??"
       "cell_name": "nch",
       "library"  : library,
       "defaults" : """
  (foo string "0n")
  (bar string "180n")
"""}

#Add any CDB static cells you want to load here
static_cell_names = ["AD2", "M1CUT", "PWelltie2", "PYM1CON", "M1M2VIA", "NWELLTIE"]
static_cells = {}
for name in static_cell_names:
   static_cells[name] = {"func"     : "pcGenCell_" + name,
       "cell_name": name,
       "library": library,
       "defaults": """
   """}

#Sometimes the code accesses strange variables that aren't even supposed to be defined. 
interp.skill.variables['labelType'] = None


#codes = ['test.il']
codes = ['cbtools2.il','cbtools.il','cb.il','creategate.il','creatediff.il','nch.il']

#Add code for static cells
for k,v in static_cells.items():
   codes.append("binary/output/" + k + ".il")

#bumping this causes all code to recompile
iversion = 17

#Load props and layermap
interp.init(layermap_file)
#load the code objects
for c in codes:
  interp.cload(c,iversion)

#Define the array of cell definitions
cells = [nch]

#Append static cell defs
for k,v in static_cells.items():
   cells.append(v)

print(cells)
interp.load_cells(cells)

#Optionally change some parameters through pcell callbacks
interp.pcell_apply('w',"500n")
interp.pcell_apply('fingers',"3")

try:
   #Run it
   interp.layout('nch')
except:
   print interp.skill.variables

   raise
print(interp.skill.variables)

interp.runtime.write()


