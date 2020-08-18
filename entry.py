#!/usr/bin/python3

import interp
import pickle
import marshal
import copyreg
import types
import os
library = "mytech"
#layermap_file = "mytech.layermap"
layermap_file = "s8rf2_dv.layermap"



paths = """./iops8a_hvxlpbt/iops8a_hvxlpbt_nor3/layout/iops8a_hvxlpbt_nor3.il
./iops8a_hvxlpbt/iops8a_hvxlpbt_buildspace/layout/iops8a_hvxlpbt_buildspace.il
./iops8a_hvxlpbt/iops8a_hvxlpbt_nand2/layout/iops8a_hvxlpbt_nand2.il
./iops8a_hvxlpbt/iops8a_hvxlpbt_inv_x1/layout/iops8a_hvxlpbt_inv_x1.il
./iops8a_hvxlpbt/iops8a_hvxlpbt_endcap/layout/iops8a_hvxlpbt_endcap.il
./iops8a_hvxlpbt/iops8a_hvxlpbt_diff_space/layout/iops8a_hvxlpbt_diff_space.il
./iops8a_hvxlpbt/iops8a_hvxlpbt_einv_x1/layout/iops8a_hvxlpbt_einv_x1.il
./iops8a_hvxlpbt/iops8a_hvxlpbt_inv_x2/layout/iops8a_hvxlpbt_inv_x2.il
./iops8a_hvxlpbt/iops8a_hvxlpbt_xor/layout/iops8a_hvxlpbt_xor.il
./iops8a_hvxlpbt/iops8a_hvxlpbt_inv_x8/layout/iops8a_hvxlpbt_inv_x8.il
./iops8a_hvxlpbt/iops8a_hvxlpbt_inv_x4/layout/iops8a_hvxlpbt_inv_x4.il
./iops8a_hvxlpbt/iops8a_hvxlpbt_csw_x1/layout/iops8a_hvxlpbt_csw_x1.il
./iops8a_hvxlpbt/iops8a_hvxlpbt_einv_x2/layout/iops8a_hvxlpbt_einv_x2.il
./iops8a_hvxlpbt/iops8a_hvxlpbt_nor/layout/iops8a_hvxlpbt_nor.il
./iops8a_hvxlpbt/iops8a_hvxlpbt_csw_x2/layout/iops8a_hvxlpbt_csw_x2.il
./iops8a_hvxlpbt/iops8a_hvxlpbt_nor2/layout/iops8a_hvxlpbt_nor2.il
./iops8a_hvlpbt/iops8a_hvlpbt_buildspace/layout/iops8a_hvlpbt_buildspace.il
./iops8a_hvlpbt/iops8a_hvlpbt_inv_x1/layout/iops8a_hvlpbt_inv_x1.il
./iops8a_hvsbt/iops8a_hvsbt_csw_x2/layout/iops8a_hvsbt_csw_x2.il
./iops8a_hvsbt/iops8a_hvsbt_inv_x1/layout/iops8a_hvsbt_inv_x1.il
./iops8a_hvsbt/iops8a_hvsbt_nand2/layout/iops8a_hvsbt_nand2.il
./iops8a_hvsbt/iops8a_hvsbt_csw_x1/layout/iops8a_hvsbt_csw_x1.il
./iops8a_hvsbt/iops8a_hvsbt_nor_x2/layout/iops8a_hvsbt_nor_x2.il
./iops8a_hvsbt/iops8a_hvsbt_inv_x2/layout/iops8a_hvsbt_inv_x2.il
./iops8a_hvsbt/iops8a_hvsbt_xor/layout/iops8a_hvsbt_xor.il
./iops8a_hvsbt/iops8a_hvsbt_diff_space/layout/iops8a_hvsbt_diff_space.il
./iops8a_hvsbt/iops8a_hvsbt_nor/layout/iops8a_hvsbt_nor.il
./iops8a_hvsbt/iops8a_hvsbt_nor3/layout/iops8a_hvsbt_nor3.il
./iops8a_hvsbt/iops8a_hvsbt_einv_x1/layout/iops8a_hvsbt_einv_x1.il
./iops8a_hvsbt/iops8a_hvsbt_inv_x8/layout/iops8a_hvsbt_inv_x8.il
./iops8a_hvsbt/iops8a_hvsbt_endcap/layout/iops8a_hvsbt_endcap.il
./iops8a_hvsbt/iops8a_top_aipcombo/layout/iops8a_top_aipcombo.il
./iops8a_hvsbt/iops8a_hvsbt_inv_x4/layout/iops8a_hvsbt_inv_x4.il
./iops8a_hvsbt/iops8a_hvsbt_buildspace/layout/iops8a_hvsbt_buildspace.il
./iops8a_hvsbt/iops8a_hvsbt_einv_x2/layout/iops8a_hvsbt_einv_x2.il
./iops8a_lvlp/iops8a_lvlp_csw_x2/layout/iops8a_lvlp_csw_x2.il
./iops8a_lvlp/iops8a_lvlp_nand2/layout/iops8a_lvlp_nand2.il
./iops8a_lvlp/iops8a_lvlp_einv_x6p_x2n/layout/iops8a_lvlp_einv_x6p_x2n.il
./iops8a_lvlp/iops8a_lvlp_buildspace/layout/iops8a_lvlp_buildspace.il
./iops8a_lvlp/iops8a_lvlp_diff_space/layout/iops8a_lvlp_diff_space.il
./iops8a_lvlp/iops8a_lvlp_einv_x1/layout/iops8a_lvlp_einv_x1.il
./iops8a_lvlp/iops8a_lvlp_xor/layout/iops8a_lvlp_xor.il
./iops8a_lvlp/iops8a_lvlp_inv_x4/layout/iops8a_lvlp_inv_x4.il
./iops8a_lvlp/iops8a_lvlp_csw_x1/layout/iops8a_lvlp_csw_x1.il
./iops8a_lvlp/iops8a_lvlp_reg_shft/layout/iops8a_lvlp_reg_shft.il
./iops8a_lvlp/iops8a_lvlp_nor2/layout/iops8a_lvlp_nor2.il
./iops8a_lvlp/iops8a_lvlp_einv_x2/layout/iops8a_lvlp_einv_x2.il
./iops8a_lvlp/iops8a_lvlp_inv_x1/layout/iops8a_lvlp_inv_x1.il
./iops8a_lvlp/iops8a_lvlp_xnor/layout/iops8a_lvlp_xnor.il
./iops8a_lvlp/iops8a_lvlp_einv_weak/layout/iops8a_lvlp_einv_weak.il
./iops8a_lvlp/iops8a_lvlp_endcap/layout/iops8a_lvlp_endcap.il
./iops8a_lvlp/iops8a_lvlp_inv_x2/layout/iops8a_lvlp_inv_x2.il
./iops8a_lvlp/iops8a_lvlp_inv_x8/layout/iops8a_lvlp_inv_x8.il
./iops8a_lvlp/iops8a_lvlp_endcap_met/layout/iops8a_lvlp_endcap_met.il""".split("\n")

#Add any CDB static cells you want to load here
static_cells = {}
codes = []
for path in paths:
   path = "~/skywater-src-nda/iops8a/20110902r/iops8a/opus/" + path
   name = path.split("/")[-1].split(".")[0]
   static_cells[name] = {"func"     : "pcGenCell_" + name,
       "cell_name": name,
       "library": library,
       "defaults": """
   """}
   path = os.path.abspath(os.path.expanduser(path))
   print(path)
   codes.append(path)


paths = ["PYM2butt_varactor.il", "DFL1sd.il", "DFL1sd2.il", "pfet_symbolic.il", "pEsdFet.il", "uhrpoly.il", "uhrpoly_0p35.il", "HRPoly_0p35_L1M1con.il", "HRPoly_0p35_RPL1con.il", "pEsdCascodeFet.il", "sub.il", "master.il"]

for path in paths:
   name = path.split(".")[0]
   static_cells[name] = {"func"     : "pcGenCell_" + name,
       "cell_name": name,
       "library": library,
       "defaults": """
  (inWell string "TRUE")
  (center string "FALSE")
"""}
   codes.append(path)

static_cells["HRPoly_0p35_L1M1con"]["defaults"] = """
(bBoxEff list   ( (-0.06 -0.06)  (2.03 0.23)))
(contactLayer string  "mcon")
(topLayerPinBbox list   ( (-0.06 -0.06)  (2.03 0.23)))
(topLayer list   ("met1" "drawing"))
(contactLayerBbox list   ( (0.0 0.0)  (1.97 0.17)))
(botLayerBbox list   ( (0.0 0.0)  (1.97 0.17)))
(botLayer list   ("li1" "drawing"))
(pin# int  2)
(layer2YEnc float  0.06)
(CenterAtOrigin bool  0)
(viaLayerImpEnc float  0.0)
(viaLayerImplant list nil)
(layer2ImpEnc float  0.0)
(layer2Implant list  nil)
(layer1ImpEnc float  0.0)
(layer1Implant list nil)
(layer1YEnc float  0.0)
(layer1XEnc float  0.0)
(maxvLayer list  nil)
(layer1 string "li1")
(layer2 string "met1")
(viaLayer string "mcon")
(encByLayer1 float  0.0)
(layer2XEnc float  0.06)
(l float  0.17)
(w float  0.17)
(yPitch float  0.36)
(xPitch float  0.36)
(column int  6)
(row int 1)
(rotateTop string "TRUE")
"""

static_cells["HRPoly_0p35_RPL1con"]["defaults"] = """
(bBoxEff list   ( (0.0 0.0)  (2.16 0.35)))
(contactLayer string  "licon1")
(topLayerPinBbox list   ( (0.0 0.0)  (2.16 0.35)))
(topLayer list  ("li1" "drawing"))
(contactLayerBbox list   ( (0.08 0.08)  (2.08 0.27)))
(botLayerBbox list   ( (0.0 0.0)  (2.16 0.35)))
(botLayer list   ("poly" "drawing"))
(pin# int  2)
(layer2YEnc float 0.08)
(CenterAtOrigin string  "FALSE")
(viaLayerImpEnc float  0.0)
(viaLayerImplant list nil)
(layer2ImpEnc float  0.0)
(layer2Implant list nil)
(layer1ImpEnc float  0.0)
(layer1Implant list nil)
(layer1YEnc float  0.0)
(layer1XEnc float  0.0)
(maxvLayer list nil)
(layer1 string  "poly")
(layer2 string  "li1")
(viaLayer string  "licon1")
(encByLayer1 float  0.08)
(layer2XEnc float  0.08)
(l float  0.19)
(w float  2.0)
(yPitch float  0.7)
(xPitch float  0.54)
(column int 1)
(row int 1)
(rotateTop string "TRUE")
"""

static_cells["DFL1sd"]["defaults"] = """
(bBoxLayer2 list ((0.055 -0.02)  (0.225 0.31)))
(description string "single nonStrap to li1")
(res float 600.0)
(topLayerPinBbox list ((0.055 -0.02)  (0.225 0.31)))
(topLayer list ("li1" "drawing"))
(bBoxVia1 list ((0.055 0.06)  (0.225 0.23)))
(diffLayerBbox list ((0.0 0.0)  (0.265 0.29)))
(diffLayer list ("diff" "drawing"))
(pin# int 2)
(wellLayerEnc float 0.18)
(snapGrid float 0.005)
(diffImpXLEnc list (0.125 0.125)) 
(centerLayer2 list nil)
(centerVia1 list nil)
(emulateSlotVia list nil)
(wellminWidth float 0.0)
(diffImpEncList list nil)
(diffCoreImpYEnc list (0.0 0.0))
(diffCoreImpXREnc list (0.0 0.0))
(diffCoreImpXLEnc list (0.0 0.0))
(diffCoreImplant list nil)
(maxvLayer list nil)
(diffLayer list ("diff" "drawing"))
(layer2 list ("li1" "drawing"))
(viaLayer list ("licon1" "drawing"))
(wellLayer string "nwell")
(viaWidth float 0.17)
(viaSpace float 0.17)
(diffREnc float 0.04)
(diffLEnc float 0.055)
(diffYEnc float 0.06)
(layer2REnc float 0.0)
(layer2LEnc float 0.0)
(layer2YEnc float 0.08)
(layer2Width float 0.17)
(diffImplant list ("nsdm" "psdm"))
(diffImpXREnc list (0.125 0.125))
(diffImpYEnc list (0.125 0.125))
(implant boolean 1)
(inWell boolean 0)
(w float 0.29)
(diffImpChoice int 0)
"""


static_cells["DFL1sd2"]["defaults"] = """
(bBoxLayer2 list ((0.055 -0.02)  (0.225 0.31)))
(description string "single nonStrap to li1")
(res float 600.0)
(topLayerPinBbox list ((0.055 -0.02)  (0.225 0.31)))
(topLayer list ("li1" "drawing"))
(bBoxVia1 list ((0.055 0.06)  (0.225 0.23)))
(diffLayerBbox list ((0.0 0.0)  (0.265 0.29)))
(diffLayer list ("diff" "drawing"))
(pin# int 2)
(wellLayerEnc float 0.18)
(snapGrid float 0.005)
(diffImpXLEnc list (0.125 0.125)) 
(centerLayer2 list nil)
(centerVia1 list nil)
(emulateSlotVia list nil)
(wellminWidth float 0.0)
(diffImpEncList list nil)
(diffCoreImpYEnc list (0.0 0.0))
(diffCoreImpXREnc list (0.0 0.0))
(diffCoreImpXLEnc list (0.0 0.0))
(diffCoreImplant list nil)
(maxvLayer list nil)
(diffLayer list ("diff" "drawing"))
(layer2 list ("li1" "drawing"))
(viaLayer list ("licon1" "drawing"))
(wellLayer string "nwell")
(viaWidth float 0.17)
(viaSpace float 0.17)
(diffREnc float 0.04)
(diffLEnc float 0.055)
(diffYEnc float 0.06)
(layer2REnc float 0.0)
(layer2LEnc float 0.0)
(layer2YEnc float 0.08)
(layer2Width float 0.17)
(diffImplant list ("nsdm" "psdm"))
(diffImpXREnc list (0.125 0.125))
(diffImpYEnc list (0.125 0.125))
(implant boolean 1)
(inWell boolean 0)
(w float 0.29)
(diffImpChoice int 0)
"""

#Sometimes the code accesses strange variables that aren't even supposed to be defined. 
interp.skill.variables['labelType'] = None

#bumping this causes all code to recompile
iversion = 17

#Load props and layermap
interp.init(layermap_file)
#load the code objects
for c in codes:
  interp.cload(c,iversion)

cells = []
for k,v in static_cells.items():
   cells.append(v)

print(cells)

interp.load_cells(cells)

#Optionally change some parameters through pcell callbacks
#interp.pcell_apply('w',"500n")
#interp.pcell_apply('fingers',"3")
#
try:
   #Run it
   interp.layout('pfet_symbolic')
except:
   print(interp.skill.variables)

   raise
print(interp.skill.variables)

interp.runtime.write()


