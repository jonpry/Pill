#!/usr/bin/python

import klayout.db as db
import klayout.lib

layout = db.Layout()
layout.dbu = .001
top = layout.create_cell("nch")

f = open("tsmcN65.layermap").read().split("\n")
layermap = {}
for l in f:
  if len(l) < 1:
     continue
  if l[0] == "#":
     continue
  l = l.split()
  if len(l) != 4:
      continue
  layermap[ (l[0],l[1]) ] = [int(l[2]),int(l[3])]
  
#print layermap
def dbCreateLabel(cell,layer,origin,text,justification,orientation,font,height):
   l1 = layermap[ (layer[0],layer[1]) ]
   l1 = layout.layer(l1[0], l1[1]) 
   t = db.DText.new(text,origin[0],origin[1])
   t.halign = 1 #center
   t.valign = 1 #center
   top.shapes(l1).insert(t)

def rodCreateRect(name,layer,width,length,origin,elementsX=1,spaceX=0):
   print layer
   l1 = layermap[ (layer[0],layer[1]) ]
   l1 = layout.layer(l1[0], l1[1]) 
   r = db.DBox.new(origin[0],origin[1],origin[0]+width,origin[1]+length)
   top.shapes(l1).insert(r)
   return { "lL" : [origin[0],origin[1]], 
            "uL" : [origin[0],origin[1]+length],  
            'lR' : [origin[0]+width,origin[1]], 
            'uR' : [origin[0]+width,origin[1]+length],
            'lC' : [origin[0],origin[1]+length/2],
            'uC' : [origin[0]+width/2,origin[1]+length],
            'dbId' : {'pin' : None}} 

def dbCreateRect(name,layer,coord):
   l1 = layermap[ (layer[0],layer[1]) ]
   l1 = layout.layer(l1[0], l1[1]) 
   r = db.DBox.new(coord[0][0],coord[0][1],coord[1][0],coord[1][1])
   top.shapes(l1).insert(r)

def addPoint(a,b):
  return [a[0]+b[0],a[1]+b[1]]

def rodFillBBoxWithRects(layer,fillBBox,width,length,spaceX,spaceY,gap="distribute"):
   assert(gap=="distribute")
   boxWidth = fillBBox[1][0] - fillBBox[0][0]
   boxHeight = fillBBox[1][1] - fillBBox[0][1]
   p = addPoint(fillBBox[0],[boxWidth/2,boxHeight/2])
   p = addPoint(p,[-width/2,-length/2])
   rodCreateRect("",layer,width,length,p)

dbCreateLabel(None,["IP","drawing"],[0,0], "& Distributor TSMC",
	    "centerCenter","R0","stick",0.0) 

rodCreateRect("gate",['PO', 'drawing'],0.060000000000000005,0.2,[0,0])
rodCreateRect('gatePinU_0', ['PO', 'drawing'], 0.060000000000000005, 0.14, [0, 0.2], 1, 0)
rodCreateRect('gatePinD_0', ['PO', 'drawing'], 0.060000000000000005, 0.14, [0, -0.14], 1, 0)
rodCreateRect('diffPinL_Gate', ['OD', 'drawing'], 0.060000000000000005, 0.2, [0.0, 0], 1, 0)

rodCreateRect('diffPinLS', ['OD', 'drawing'], 0.175, 0.2, [-0.175, 0], 1, 0)
rodCreateRect('metal_0', ['M1', 'drawing'], 0.09, 0.22000000000000003, [-0.145, -0.01], 1, 0)
dbCreateLabel(None, ['text', 'drawing'], [-0.09999999999999999, 0.10000000000000002], 'S', 'centerCenter', 'R0', 'stick', 0.05)
rodFillBBoxWithRects(layer=['CO', 'drawing'], fillBBox=[[-0.145, 0.03], [-0.05499999999999999, 0.17]], width= 0.09, length=0.09, spaceX= 0.11, spaceY=0.11)


rodCreateRect('diffPinRD', ['OD', 'drawing'], 0.175, 0.2, [0.060000000000000005, 0], 1, 0)
rodCreateRect('metal_1', ['M1', 'drawing'], 0.09, 0.22000000000000003,  [0.115, -0.01], 1, 0)
dbCreateLabel(None,['text', 'drawing'], [-0.09999999999999999, 0.10000000000000002], 'S', 'centerCenter', 'R0', 'stick', 0.05)
rodFillBBoxWithRects(layer=['CO', 'drawing'], fillBBox=[[0.115, 0.03], [0.20500000000000002, 0.17]], width=0.09, length= 0.09, spaceX= 0.11, spaceY= 0.11)


dbCreateRect(None,['NP', 'drawing'], [[-0.305, -0.34], [0.36500000000000005, 0.54]])
rodCreateRect('body', ['PDK', 'drawing'], 0.8500000000000001, 0.64, [-0.395, -0.22], 1, 0)

dbCreateRect(None,['LVSDMY', 'dummy1'], [[-0.395, -0.22], [0.45500000000000007, 0.42000000000000004]])
dbCreateRect(None,['VTL_N', 'drawing'], [[-0.185, -0.16], [0.245, 0.36]])

#dbCreateRect(None,['instance', 'drawing'], [[-0.175, 0], [0.23500000000000001, 0.2]])


layout.write("foo.gds")
