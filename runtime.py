#Copyright (C) 2019 Jon Pry
#
#This file is part of Pill.
#
#Pill is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 2 of the License, or
#(at your option) any later version.
#
#Pill is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with Pill.  If not, see <http://www.gnu.org/licenses/>.

import inspect
import sys
import os
import re
import props
from tools import Lazy

import klayout.db as db
import klayout.lib
import tools
import math
import context
import geom
import uuid

layout = db.Layout()
layout.dbu = .001

######## These are implementations of Skill standard library functions
def getsqg(*s):
   print("*****GetSqG" + str(len(s)))
   ret = None
   print(s)
   l = s[0]

   if not l:
      return l

   if isinstance(l,props.PropertyDict):
      print("was property dict")
      if s[1] in l:
        ret = l[s[1]]
      else:
        l = list(l.values())

   if not ret:
      if not isinstance(l,list):
         print("not list")
         if s[1] in l:
           ret = l[s[1]]
      else:
         print("was list")
         ret = []
         for e in l:
            if len(s) > 1 and s[1] in e:
               ret.append(e[s[1]])
         if len(ret) == 1:
            ret = ret[0]
         if len(ret) == 0:
            ret = None
   if len(s) > 2:
      ret = getsqg(*([ret] + list(s[2:])))
   print("*****GetSqG ret")
   print(ret)
   return ret

def setsqg(a,b):
   #assert(False)
   pass

def stringp(s):
   return isinstance(s,str) or isinstance(s,props.StringProperty)

def floatp(s):
   print("floatp")
   print(type(s))
   print(s)
   return isinstance(s,float)

def fixp(s):
   return isinstance(s,int) and not (isinstance(s,bool) or isinstance(s,props.BooleanProperty))

def numberp(s):
   return fixp(s) or isinstance(s,float)

def boundp(e):
   return e.expr in skill.variables

def greaterp(a,b):
   return a > b

def makeTable(name,default):
   return tools.SkillTable(name,default)

def mod(a,b):
   return a % b

def fix(a):
   r = int(math.floor(a))
   print("floor: " + str(a) + "=" + str(r))
   return r

def dbGet(a,b):
   print(b)
   if b in context.bag:
      print(context.bag[b])
      return context.bag[b]
   else:
      return None

def sprintf(foo,format,*args):
   nargs = []
   for i in range(len(args)):
      if isinstance(args[i],Lazy):
         nargs.append(args[i].deref()) 
      else:
         nargs.append(args[i])
      if nargs[i] == None:
         nargs[i] = 0;
   nargs=tuple(nargs) 
   print(format)
   print(nargs)
   return format.replace("%L","%s") % nargs

def printf(format, *args):
   print("DBG print")
   print(format)
   #sys.stdout.write(sprintf(None,format,*args))

def artError(format, *args):
   sys.stdout.write(sprintf(None,format,*args))
   assert(False)
   exit(0)

def listl(*args,**kwargs):
   if len(kwargs.keys()):
      assert(len(args) == 0)
      return kwargs
   print("listl: " + str(args))
   return list(args)

def car(l):
   print(l)
   if isinstance(l,list) or isinstance(l,tools.Lazy):
      return l[0]
   return l

def cadr(l):
   return car(cdr(l))

def caar(l):
   return car(car(l))

def cadar(l):
   return car(cdr(car(l)))

def cadadr(l):
   return car(cdr(car(cdr(l))))

def caadr(l):
   return car(car(cdr(l)))

def cdr(l):
   return l[1:]

def cddr(l):
   return cdr(cdr(l))

def cdddr(l):
   return cdr(cdr(cdr(l)))

def caddr(l):
   return car(cdr(cdr(l)))

def cadddr(l):
   return car(cdr(cdr(cdr(l))))

def cddddr(l):
   return car(cdr(cdr(cdr(cdr(l)))))

def yCoord(l):
   return l[1]

def evalstring(s):
   print("eval: " + s)
   v = interp(s)
   print(v)
   return v

def techGetParam(db,ob):
   techParms = { "cadGrid" : 0.005 }
   return techParms[ob]

def cdfParseFloatString(s):
   print("cdfParseFloatString: " + str(s) + ", " + str(s[-1]) + ", " + str(type(s)))
   for i in range(len(s)):
     print(str(s[i]))

   try:
     return float(s)
   except:
     pass

   postfix = 1.0
   if s[-1] == "n":
      postfix = 1e-9 
      s=s[:-1]
   elif s[-1] == "u":
      postfix = 1e-6 
      s=s[:-1]
   elif s[-1] == "m":
      postfix = 1e-3 
      s=s[:-1]
   try:
      v = float(s)*postfix
   except:
      print("*******" + s)
      raise
   print("cdfFloat: " + str(v))
   return v

def maplayer(layer):
   print(layer[0])
   if not isinstance(layer,list):
      print("drawing")
      layer = [layer, "drawing"]

   if isinstance(layer[0],int):
      return layout.layer(int(layer[0]),int(layer[1])) #TODO: handle purpose

   if (layer[0],layer[1]) in layermap:
      l1 = layermap[ (layer[0],layer[1]) ]
      print("layer: " + str(l1))
      l1 = layout.layer(l1[0], l1[1])  
      return l1
   return -1

def rodCreateRectBase(layer,width,length,origin=[0,0],elementsX=1,spaceX=0,termIOType=None,termName=None,pin=None,cvId=None,beginOffset=0,endOffset=0,space=0,subs=None):
   r = None
   l1 = maplayer(layer)
   if not subs:
      subs = []
   if l1 >= 0:
      print("found layer")
      r = db.DBox.new(origin[0],origin[1],origin[0]+width,origin[1]+length).to_itype(0.001)
      r = top.shapes(l1).insert(r)
   subs.append(r)
   return createObj(subs=subs)

rodsByName = {}
def rodCreateRect(layer,width=0,length=0,origin=[0,0],name="",elementsX=1,elementsY=1,spaceX=0,spaceY=0,termIOType=None,
                  termName=None,pin=None,cvId=None,beginOffset=0,endOffset=0,space=0,fromObj=None,bBox=None,pinLabel=None,pinLabelLayer=None,subRectArray=None,size=0):
   #if subRectArray:
   #   return
   if fromObj:
      width=fromObj['width']+size
      length=fromObj['length']+size
      origin=fromObj['lL']
      origin[0] -= size/2
      origin[1] -= size/2

   if bBox:
     origin = bBox[0]
     width = bBox[1][0] - bBox[0][0]
     length = bBox[1][1] - bBox[0][1]
      
   flocals = locals()
   print("rodCreateRect: " + str([arg + ":" + str(flocals[arg]) for arg in inspect.getargspec(rodCreateRect).args]))
   objs = []
   subs = []
    
   if subRectArray:
      assert(elementsX==1 and elementsY==1)
      for subRect in subRectArray:
          torigin = origin[:]
          twidth = width
          tlength = length
          if "lowerLeftOffsetY" in subRect:
             ofst = subRect["lowerLeftOffsetY"]
             print("lowerLeftOffsetY: " + str(ofst))
             tlength -= ofst
             torigin[1] += ofst/2
          if "upperRightOffsetY" in subRect:
             ofst = subRect["upperRightOffsetY"]
             tlength += ofst
             torigin[1] -= ofst/2
             print("upperRightOffsetY: " + str(ofst))
          if "lowerLeftOffsetX" in subRect:
             ofst = subRect["lowerLeftOffsetX"]
             twidth -= ofst
             torigin[0] += ofst/2
          if "upperRightOffsetX" in subRect:
             ofst = subRect["upperRightOffsetX"]
             twidth += ofst
             torigin[0] -= ofst/2

          swidth = subRect["width"]
          slength = subRect["length"]
          sspaceX = subRect["spaceX"]
          sspaceY = subRect["spaceY"]
          assert(subRect["gap"] == "minimum")
          telementsX, fooX = maxNinN(twidth,swidth,sspaceX)
          telementsY, fooY = maxNinN(tlength,slength,sspaceY)
          for x in range(telementsX):
             for y in range(telementsY):
                p = addPoint(torigin,[x * (sspaceX+swidth), y * (sspaceY+slength)])
                l1 = maplayer(subRect["layer"])
                if l1 >= 0:
                   print("found layer")
                   r = db.DBox.new(p[0],p[1],p[0]+swidth,p[1]+slength).to_itype(0.001)
                   r = top.shapes(l1).insert(r)
                   subs.append(r)
           

   for x in range(elementsX):
      for y in range(elementsY):
         p = addPoint(origin,[x * (spaceX+width), y * (spaceY+length)])
         objs.append(rodCreateRectBase(layer,width,length,origin=p,subs=subs))

   objs.reverse()
   if len(objs)==1:
      print(objs[0])
      rodsByName[name] = objs[0]
      return objs[0]
   rodsByName[name] = objs
   return objs

def rodTranslate(alignObj,delta,internal=False,done=None):
   m = ["lowerLeft","lL", "upperLeft", "uL", "lowerRight", "lR", "upperRight", "uR", "lC", 
         "uC", "cC", "cR", "cL"]
   for h in m:
      alignObj[h] = addPoint(alignObj[h],delta)
   print("ao: " + str(alignObj))
   shapes = alignObj['_shapes']
   print("shapes: " + str(shapes))
   if not internal:
      done = set()
   for s in shapes:
      print("s: " + str(s))
      s.transform(db.DTrans.new(float(delta[0]),float(delta[1])))
   done.add(alignObj['_id'])
 
   for m in alignObj['_masters']:
      if not m['_id'] in done:
         rodTranslate(m,delta,True,done)
   for s in alignObj['_slaves']:
      if not s['_id'] in done:
         rodTranslate(s,delta,True,done)

def rodAlign(alignObj,alignHandle,refObj=None,refHandle=None,ySep=0,xSep=0,refPoint=None):
   print("ref: " + str(refObj))
   print("alg: " + str(alignObj))
   print("pnt: " + str(refPoint))

   flocals = locals()
   print("rodAlign: " + str([arg + ":" + str(flocals[arg]) for arg in inspect.getargspec(rodAlign).args]))
   if not refObj and not alignObj:
       return

   m = { "lowerLeft" : "lL", "upperLeft" : "uL", "lowerRight" : "lR", "upperRight" : "uR", "lowerCenter" : "lC", 
         "upperCenter" : "uC", "centerCenter" : "cC", "centerRight" : "cR", "centerLeft" : "cL"}
   try:
      alignHandle = m[alignHandle]
   except:
      pass
   try:
      refHandle = m[refHandle]
   except:
      pass

   if refObj:
      refPoint=refObj[refHandle]

   delta = subPoint(refPoint,alignObj[alignHandle])
   delta = addPoint(delta,[xSep,ySep])
   print("Align: " + str(delta))
 
   rodTranslate(alignObj,delta)
   if refObj:
      alignObj['_masters'].append(refObj)
      refObj['_slaves'].append(alignObj)

def leftEdge(rod):
   return rod['lL'][0]

def topEdge(rod):
   return rod['uR'][1]

def bottomEdge(rod):
   return rod['lL'][1]

def rightEdge(rod):
   return rod['uR'][0]

def addPoint(a,b):
  return [a[0]+b[0],a[1]+b[1]]

def subPoint(a,b):
  return [a[0]-b[0],a[1]-b[1]]

def maxNinN(limit,obj,space):
   n = int(limit / (obj + space))
   #sometimes an extra can fit
   if n*space + (n+1)*obj <= limit:
      n += 1

   if n <= 1: 
      space = (limit - n * obj)/2
   else:
      space = (limit - n * obj) / (n-1)
   return (n,space)

def rodFillBBoxWithRects(layer,fillBBox,width,length,spaceX,spaceY,gap="distribute",cvId=None):
   print("filBbox")
   assert(gap=="distribute")
   origin = fillBBox[0]
   bwidth = fillBBox[1][0] - fillBBox[0][0]
   blength = fillBBox[1][1] - fillBBox[0][1]


   p = addPoint(origin,[bwidth/2,0])
   p = addPoint(p,[-width/2,0])
   rects = []

   ny,spaceY = maxNinN(blength,length,spaceY)

   for i in range(ny):
      rects = rects + rodCreateRect(layer,width,length,p)['_shapes']
      p[1] += spaceY + length

   return createObj(subs=rects)

def createObj(dbox=None,subs=None):
   if not(dbox or (subs and len(subs) > 0 and subs[0])):
       return None
   print("dbox: " + str(dbox))
   if subs:
      for s in subs:
         if dbox:
            dbox = dbox + s.dbbox()
         else:
            dbox = s.dbbox()

   ibox = dbox.to_itype(0.001)
   dbox = ibox.to_dtype(0.001)
   origin = [dbox.p1.x,dbox.p1.y]
   twidth = (ibox.p2.x-ibox.p1.x)*0.001
   tlength = (ibox.p2.y-ibox.p1.y)*0.001
 
   if twidth > .09999999 and twidth < .1:
      print("%.20e %.20e %.20e %d %d %.20e %.20e" % (twidth, dbox.p2.x, dbox.p1.x, ibox.p2.x, ibox.p1.x, 105*.001, 5*.001))
      assert(False)
   if not subs:
       subs = []
   obj = {  "lL" : [origin[0],origin[1]], 
            "uL" : [origin[0],origin[1]+tlength],  
            'lR' : [origin[0]+twidth,origin[1]], 
            'uR' : [origin[0]+twidth,origin[1]+tlength],
            'lC' : [origin[0]+twidth/2,origin[1]],
            'uC' : [origin[0]+twidth/2,origin[1]+tlength],
            'cC' : [origin[0]+twidth/2,origin[1]+tlength/2],
            'cR' : [origin[0]+twidth,origin[1]+tlength/2],
            'cL' : [origin[0],origin[1]+tlength/2],
            'length' : tlength,
            'width' : twidth,
            'dbId' : {'pin' : None},
            '_shapes' : subs,
            '_slaves' : [],
            '_masters' : [],
            '_transform' : None,
            '_id' : uuid.uuid1(),
            '_ttype' : 'ROD'} 
   obj['lowerLeft'] = obj['lL']
   obj['lowerRight'] = obj['lR']
   obj['upperRight'] = obj['uR']
   obj['upperLeft'] = obj['uL']
   obj['bBox'] = [[origin[0],origin[0]+twidth],[origin[1],origin[1]+tlength]]
   print("createObj: " + str(obj))
   return obj

def rodCreatePath(layer,width,pts,termIOType=None,termName=None,pin=None,subRect=None,name="",justification="center"):
  subs = []
  print("createPath: " + str(pts) + ", layer: " + str(layer) + ", sub: " + str(subRect) + ", just: " + justification)

  r = None
  if (layer[0],layer[1]) in layermap:
      l1 = maplayer(layer)
      assert(l1 >= 0)
      dpts = []
      for p in pts:
        dpts.append(db.DPoint.new(p[0],p[1]))  
      r = geom.Path(dpts,width,justification)
      r = top.shapes(l1).insert(r)
      subs.append(r)

  if subRect:
    assert(len(pts) == 2)

    assert(env['distributeSingleSubRect'])
    assert(len(subRect)==1)
    for s in subRect:
       n,space = maxNinN(width+s['beginOffset']+s['endOffset'],width,s['space'])
       s['elementsX'] = n
       s['spaceX'] = space
       #s['pin'] = pin
       sub = rodCreateRect(**s)
       if n==1:
          sub = [sub]
       for e in sub:
          rodTranslate(e,[-width/2,-width/2])
          if n==1:
             rodTranslate(e,[twidth/2,0])
          else:
             rodTranslate(e,[-s['beginOffset']+width/2,0])
          subs = subs + e['_shapes']


  obj = createObj(subs=subs)

  print("Path: " + str(obj))
  rodsByName[name] = obj
  return obj

def rodAddPoints(a,b):
   return [a[0]+b[0],a[1] + b[1]]

def rodAddToY(a,b):
   return [a[0],a[1] + b]

def rodAddToX(a,b):
   return [a[0]+b,a[1]]


def rodCreatePolygon(name,layer,fromObj=None):
   print("rodCreatePolygon: \"" + name + "\", " + str(layer))
   l1 = maplayer(layer)
   assert(l1 >= 0)  
   r = db.DPolygon.new(db.DBox.new(fromObj['lL'][0],fromObj['lL'][1],fromObj['uR'][0],fromObj['uR'][1]))
   r = top.shapes(l1).insert(r)

   obj = createObj(subs=[r])
   rodsByName[name] = obj
   return obj

def dbCreatePolygon(cv,layer,pts):
   print("dbCreatePolygon: \"" + str(cv) + "\", " + str(layer))
   l1 = maplayer(layer)
   assert(l1 >= 0)  
   dpts = []
   for p in pts:
      dpts.append(db.DPoint.new(p[0],p[1]))  
   r = db.DPolygon.new(dpts)
   r = top.shapes(l1).insert(r)

def rodAssignHandleToParameter(**kwargs):
   print("assignHandle: " + str(kwargs))
   return None

def rodGetObj(i):
   print("rodGetObject: " + str(i))
   if '_ttype' in i:
      if i['_ttype'] == "ROD":
          return i


   print(rodsByName.keys())
   if i in rodsByName:
      print(rodsByName[i])
      return rodsByName[i]

   s = i.split("/")
   if len(s) > 1:
     tx = []
     print("rod subobject query: " + str(s))
     cmap = rodsByName
     inst = rodsByName[s[0]]
     dbox = None
     got_shape=False
     for e in s:
        e = cmap[e]
        cell = e['_shapes'][0]
        if isinstance(cell,db.Instance):
           cmap = rod_map[cell.cell.basic_name()]
           tx.append(cell.dtrans)
        else:
           got_shape=True
        dbox = e['_shapes'][0].dbbox()
     #accumulate the transforms
     if not got_shape:
        print(dbox)
        dbox.p1 = db.DPoint.new(0,0) #If only have a cell, then all stuff relative to origin
        dbox.p2 = dbox.p1
     total = db.DTrans()
     for t in tx:
        total = total * t
     if not dbox:
        write()
        exit()
     dbox = total.trans(dbox)
     obj = createObj(dbox=dbox)
     obj['_slaves'].append(inst)
     inst['_masters'].append(obj)
     obj['_transform'] = total
     rodsByName[i] = obj
     return obj
   write()
   assert(False)
   exit(0)
   print("****************getObject failed")
   return None

def rodPointX(l):
   return l[0]

def rodPointY(l):
   return l[1]

def snapToGrid(v,g):
   ret = round(v/float(g))*g
   return ret

#dbCreateLabel(cv 4 1:1 "myLabel" "centerLeft" "R0" "roman" 2)
def dbCreateLabel(cell,layer,origin,text,justification=None,orientation=None,font=None,height=1):
   l1 = maplayer(layer)
   t = db.DText.new(text,origin[0],origin[1])
   t.size = height
   t.halign = 1 #center
   t.valign = 1 #center
   top.shapes(l1).insert(t)
   flocals = locals()
   print("createLabel: " + str([flocals[arg] for arg in inspect.getargspec(dbCreateLabel).args]))

def dbOpenCellViewByType(lib,cell,purpose,t):
   print("dbOpenCellViewByType: " + cell)
   ret = { 'name' : cell, 'isParamCell' : True}
   ret.update(iprops(cell))
   return ret

def dbOpenCellView(lib,cell,purpose,t,m):
   print("dbOpenCellView: " + cell)
   ret = { 'name' : cell, 'isParamCell' : True}
   ret.update(iprops(cell))
   return ret

def dbCreateRect(cell,layer,coord):
   print("dbCreateRect: " + str(layer) + ", " + str(coord))
   return rodCreateRect(layer,coord[1][0] - coord[0][0],coord[1][1] - coord[0][1],coord[0])

def getRot(o):
   if o == "R0":
      return 0
   if o == "MY": #TODO
      return 0
   if o == "R90":
      return 1
   if o == "R180":
      return 2
   if o == "R270":
      return 3
   print(o)
   assert(False)

def dbCreateParamInst(view, master, name, origin, orient, num=1, parm=None, phys=False):
   cell = master['name']
   print("dbCreateParamInst: \"" + str(cell) + "\", " + str(name) + ", " + str(origin) + "," + str(orient))

   assert(num==1) 

   kobj = ilayout(cell,parm)
   if not kobj:
      print("Instantiation failed")
      assert(False)
      return None
   dcell = db.DCellInstArray.new(kobj.cell_index(),db.DTrans.new(getRot(orient),False,float(origin[0]),float(origin[1])))
   dcell = top.insert(dcell)

   rodobj = createObj(subs=[dcell])
   rodsByName[name] = rodobj
   rodobj['master'] = master
   return rodobj

def dbCreateParamInstByMasterName(view, lib, cell, purpose, name, origin, orient, num=1, params=None, phys=False):
   print("paraminst")
   dbCreateParamInst(view,cell,name,origin,orient,num,params,phys)
   return True

def dbCreateInstByMasterName(view, lib, cell, purpose, name, origin, orient="R0"):
   print("createinst")
   dbCreateParamInst(view,cell,name,origin,orient,1,None)
   return True

def get_pname(s):
   print("get_pname: " + str(s))
   return s

env = {}
def envSetVal(domain,key,t,v):
   env[key] = v

def concat(*args):
   ret = ""
   for a in args:
      ret += str(a)
   print("Concat: " + ret)
   return ret

def rexMatchp(r,s):
   return re.match(r,s)

def nullfunc(*args):
   return None

def oddp(v):
   return v%2==1

def evenp(v):
   return v%2==0

def minus(a,b=None):
   if b is None:
     return -a
   return a-b

def listp(v):
   return isinstance(v,list)

def isCallable(l):
   if not l.expr in skill.procedures:
      return False
   return not not skill.procedures[l.expr]

def cons(a,b):
   if isinstance(a,Lazy):
     a = a.deref()
   if isinstance(b,Lazy):
     b = b.deref()

   if isinstance(a,list):
     return a+b
   if isinstance(b,list):
     return [a] + b
   if not b:
     return [a]
   return [a,b]

def parseString(s,t=None):
   if not t:
      return s.split()
   return s.split(t)

def strcat(*a):
   ret = ""
   for e in a:
     ret += e
   return ret

def mapcar(l, v):
   assert(False)

def nth(i,l): #TODO: not sure about this
   if isinstance(l,Lazy):
      print(l.expr)
   #   l = interp(l.expr)
   return l[int(i)]

def getLast(l):
   if not l:
     return l
   return l[-1]

def typep(v):
#TODO: handle props
   if isinstance(v,float):
      return Lazy('flonum',evalstring)
   if isinstance(v,str):
      return Lazy('string',evalstring)
   if isinstance(v,list):
      return Lazy('list',evalstring)
   if isinstance(v,int):
      return Lazy('fixnum',evalstring)
   print(type(v))
   assert(False) #TODO:

def null(v):
   return not v

def length(l):
   print("length")
   if l is None:
      return 0
   return len(l)
 
def append(a,b):
   if not a:
      a = []
   a.append(b)
   return a

def getq(a,b):
   return a[b]

def eval(v):
#TODO: handle props
   if isinstance(v,Lazy):
      return interp(v.expr)
   if isinstance(v,str):
      return skill.variables[v]
   return v

def writeout(a):
   write()
   exit(0)

def ddGetObjReadPath(o):
   return "."

def close(f):
   f.close()

def _gets(f):
   s = f.readline()
   if s == "":
      return None
   return s

def substring(s,b,l):
  return s[(b-1):][:l]

def findFunc(name):
   def find(*args):
      print("********************" + name)
      print(args)
      assert(False)
      exit(0)
   return find

######################End skill function impls

def write():
   layout.write("foo.gds")

layermap = {}
def run(layermap_file,s,r,l,p):
   global skill, interp, layermap, ilayout, iprops

   skill = s
   interp = r
   ilayout = l
   iprops = p

   f = open(layermap_file).read().split("\n")
   for l in f:
     if len(l) < 1:
       continue
     if l[0] == "#":
       continue
     l = l.split()
     if len(l) != 4:
       continue
     layermap[ (l[0],l[1]) ] = [int(l[2]),int(l[3])]

   skill.procedures['stringp'] = stringp
   skill.procedures['floatp'] = floatp
   skill.procedures['numberp'] = numberp
   skill.procedures['fixp'] = fixp
   skill.procedures['listp'] = listp
   skill.procedures['boundp'] = boundp
   skill.procedures['zerop'] = nullfunc
   skill.procedures['greaterp'] = greaterp
   skill.procedures['null'] = null
   skill.procedures['error'] = findFunc('error')
   skill.procedures['errset'] = nullfunc
   skill.procedures['makeTable'] = makeTable
   skill.procedures['dbGet'] = dbGet
   skill.procedures['mod'] = mod
   skill.procedures['getq'] = getq
   skill.procedures['fix'] = fix
   skill.procedures['printf'] = printf
   skill.procedures['list'] = listl
   skill.procedures['car'] = car
   skill.procedures['member'] = findFunc('member')
   skill.procedures['xCoord'] = car
   skill.procedures['cadr'] = cadr
   skill.procedures['cdr'] = cdr
   skill.procedures['caddr'] = caddr
   skill.procedures['cddr'] = cddr
   skill.procedures['cdddr'] = cdddr
   skill.procedures['caadr'] = caadr
   skill.procedures['cadddr'] = cadddr
   skill.procedures['cddddr'] = cddddr
   skill.procedures['caar'] = caar
   skill.procedures['cadar'] = cadar
   skill.procedures['cadadr'] = cadadr
   skill.procedures['yCoord'] = yCoord
   skill.procedures['envSetVal'] = envSetVal
   skill.procedures['ddGetObj'] = nullfunc
   skill.procedures['dbOpenBag'] = nullfunc
   skill.procedures['techGetTechFile'] = nullfunc
   skill.procedures['sprintf'] = sprintf
   skill.procedures['evalstring'] = evalstring
   skill.procedures['techGetParam'] = techGetParam
   skill.procedures['cdfParseFloatString'] = cdfParseFloatString
   skill.procedures['max'] = max
   skill.procedures['min'] = min
   skill.procedures['sqrt'] = math.sqrt
   skill.procedures['log'] = math.log
   skill.procedures['snapToGrid'] = snapToGrid
   skill.procedures['dbCreateLabel'] = dbCreateLabel
   skill.procedures['dbCreateRect'] = dbCreateRect 
   skill.procedures['dbCloseBag'] = nullfunc
   skill.procedures['dbClose'] = nullfunc
   skill.procedures['dbReplaceProp'] = nullfunc
   skill.procedures['rodCreateRect'] = rodCreateRect  
   skill.procedures['rodAddToY'] = rodAddToY
   skill.procedures['rodAddToX'] = rodAddToX
   skill.procedures['rodAssignHandleToParameter'] = rodAssignHandleToParameter
   skill.procedures['rodGetObj'] = rodGetObj
   skill.procedures['rodPointX'] = rodPointX
   skill.procedures['rodPointY'] = rodPointY
   skill.procedures['leftEdge'] = leftEdge
   skill.procedures['bottomEdge'] = bottomEdge
   skill.procedures['topEdge'] = topEdge
   skill.procedures['rightEdge'] = rightEdge
   skill.procedures['rodFillBBoxWithRects'] = rodFillBBoxWithRects
   skill.procedures['rodAddPoints'] = rodAddPoints
   skill.procedures['rodAlign'] = rodAlign
   skill.procedures['rodCreatePath'] = rodCreatePath
   skill.procedures['rodCreatePolygon'] = rodCreatePolygon
   skill.procedures['get_pname'] = get_pname
   skill.procedures['concat'] = concat
   skill.procedures['rexMatchp'] = rexMatchp
   skill.procedures['oddp'] = oddp
   skill.procedures['evenp'] = evenp
   skill.procedures['isCallable'] = isCallable
   skill.procedures['dbSetq'] = nullfunc
   skill.procedures['cons'] = cons
   skill.procedures['xcons'] = findFunc('xcons')
   skill.procedures['append'] = append
   skill.procedures['mapcar'] = mapcar
   skill.procedures['dbExternallyConnectPins'] = nullfunc
   skill.procedures['dbWeaklyConnectPins'] = nullfunc
   skill.procedures['parseString'] = parseString
   skill.procedures['strcat'] = strcat
   skill.procedures['typep'] = typep
   skill.procedures['abs'] = abs
   skill.procedures['artError'] = artError
   skill.procedures['eval'] = eval
   skill.procedures['float'] = float
   skill.procedures['nth'] = nth
   skill.procedures['index'] = findFunc('index')
   skill.procedures['round'] = round
   skill.procedures['floor'] = math.floor
   skill.procedures['ceiling'] = math.ceil
   skill.procedures['minus'] = minus   
   skill.procedures['getLast'] = getLast
   skill.procedures['length'] = length
   skill.procedures['exp'] = math.exp
   skill.procedures['errsetstring'] = nullfunc
   skill.procedures['infile'] = open
   skill.procedures['ddGetObjReadPath'] = ddGetObjReadPath
   skill.procedures['getShellEnvVar'] = findFunc('getShellEnvVar')
   skill.procedures['_gets'] = _gets
   skill.procedures['isPreSet'] = findFunc('isPreSet')
   skill.procedures['isFile'] = os.path.isfile
   skill.procedures['close'] = close
   skill.procedures['exit'] = exit
   skill.procedures['substring'] = substring
   skill.procedures['dbCreateParamInstByMasterName'] = dbCreateParamInstByMasterName
   skill.procedures['dbOpenCellViewByType'] = dbOpenCellViewByType
   skill.procedures['dbOpenCellView'] = dbOpenCellView
   skill.procedures['dbCreateParamInst'] = dbCreateParamInst
   skill.procedures['dbCreateInst'] = findFunc('dbCreateInst')
   skill.procedures['dbCreateInstByMasterName'] = dbCreateInstByMasterName
   skill.procedures['dbFlattenInst'] = findFunc('dbFlattenInst')
   skill.procedures['writeout'] = writeout #for debugging
   skill.procedures['pcExprToProp'] = nullfunc
   skill.procedures['dbAddFigToNet'] = nullfunc
   skill.procedures['dbMakeNet'] = nullfunc
   skill.procedures['dbFindTermByName'] = nullfunc
   skill.procedures['dbCreateTerm'] = nullfunc
   skill.procedures['dbCreatePin'] = nullfunc
   skill.procedures['dbCreatePolygon'] = dbCreatePolygon
   skill.procedures['dbCreatePath'] = nullfunc
   skill.procedures['dbDeleteObject'] = nullfunc
   skill.procedures['dbCreateProp'] = nullfunc
   skill.procedures['dbCreateNet'] = nullfunc
   skill.procedures['dbCreateTerm'] = nullfunc
   skill.procedures['dbLayerOr'] = nullfunc

def load_props(props_file):
   context.props = props.load_props(props_file)
   context.bag = context.props['props']

top_stack = []
rod_stack = []
rod_map = {}
top = None
def push_cell(h):
   global top, top_stack, rodsByName, rod_stack
   top_stack.append(top)
   top = layout.create_cell(h) 
   rod_stack.append(rodsByName)
   rodsByName = {}

def pop_cell():
   global top, top_stack, rodsByName, rod_stack, rod_map   
   cell = top
   oldRod = rodsByName
   top = top_stack[-1]
   top_stack = top_stack[:-1]
   rodsByName = rod_stack[-1]
   rod_stack = rod_stack[:-1] 
   rod_map[cell.basic_name()] = oldRod  
   return cell
