import inspect
import sys
import os
import re
from props import *
from tools import Lazy

import klayout.db as db
import klayout.lib
import tools
import math

layout = db.Layout()
layout.dbu = .001
top = layout.create_cell("nch")

######## These are implementations of Skill standard library functions
def stringp(s):
   return isinstance(s,basestring)

def floatp(s):
   return isinstance(s,float)

def fixp(s):
   return isinstance(s,int)

def boundp(e):
   return e.expr in skill.variables

def makeTable(name,default):
   return tools.SkillTable(name,default)

def mod(a,b):
   return a % b

def fix(a):
   return int(a)

def dbGet(a,b):
   print b
   if b in bag:
      print bag[b]
      return bag[b]
   else:
      return None

def sprintf(foo,format,*args):
   return format.replace("%L","%s") % args

def printf(format, *args):
   sys.stdout.write(sprintf(None,format,*args))

def artError(format, *args):
   sys.stdout.write(sprintf(None,format,*args))
   assert(False)
   exit(0)

def listl(*args,**kwargs):
   if len(kwargs.keys()):
      assert(len(args) == 0)
      return kwargs
   print "listl: " + str(args)
   return list(args)

def car(l):
   print l
   return l[0]

def cadr(l):
   return l[1]

def cdr(l):
   return l[1:]

def caddr(l):
   return l[2]

def cadddr(l):
   return l[3]

def yCoord(l):
   return l[1]

def evalstring(s):
   print "eval: " + s
   v = interp(s)
   print v
   return v

def techGetParam(db,ob):
   techParms = { "cadGrid" : 0.005 }
   return techParms[ob]

def cdfParseFloatString(s):
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
   v = float(s)*postfix
   print "cdfFloat: " + str(v)
   return v

def maplayer(layer):
   if not isinstance(layer,list):
      layer = [layer, "drawing"]
   if (layer[0],layer[1]) in layermap:
      l1 = layermap[ (layer[0],layer[1]) ]
      l1 = layout.layer(l1[0], l1[1])  
      return l1
   return None

def rodCreateRectBase(layer,width,length,origin=[0,0],elementsX=1,spaceX=0,termIOType=None,termName=None,pin=None,cvId=None,beginOffset=0,endOffset=0,space=0):
   r = None
   l1 = maplayer(layer)
   if l1:
      r = db.DBox.new(origin[0],origin[1],origin[0]+width,origin[1]+length)
      r = top.shapes(l1).insert(r)
   return createObj(origin,width,length,[r])

rodsByName = {}
def rodCreateRect(layer,width,length,origin=[0,0],name="",elementsX=1,elementsY=1,spaceX=0,spaceY=0,termIOType=None,termName=None,pin=None,cvId=None,beginOffset=0,endOffset=0,space=0):
   print "createRect: " + str([locals()[arg] for arg in inspect.getargspec(rodCreateRect).args])
   objs = tools.DerefList()
   for x in range(elementsX):
      for y in range(elementsY):
         p = addPoint(origin,[x * (spaceX+width), y * (spaceY+length)])
         objs.append(rodCreateRectBase(layer,width,length,origin=p))
    
   objs.reverse()
   if len(objs)==1:
      rodsByName[name] = objs[0]
      return objs[0]
   rodsByName[name] = objs
   return objs

def rodTranslate(alignObj,delta):
   m = { "lowerLeft" : "lL", "upperLeft" : "uL", "lowerRight" : "lR", "upperRight" : "uR", "lowerCenter" : "lC", 
         "upperCenter" : "uC", "centerCenter" : "cC", "centerRight" : "cR", "centerLeft" : "cL"}
   for h in m.values():
      alignObj[h] = addPoint(alignObj[h],delta)
   print "ao: " + str(alignObj)
   shapes = alignObj['_shapes']
   print "shapes: " + str(shapes)
   for s in shapes:
      print "s: " + str(s)
      s.transform(db.DTrans.new(float(delta[0]),float(delta[1])))
   for s in alignObj['_slaves']:
      rodTranslate(s,delta)

def rodAlign(refObj,alignObj,alignHandle,refHandle,ySep=0,xSep=0):
   #assert(ySep==0)
   #assert(xSep==0)
   print "ref: " + str(refObj)
   print "alg: " + str(alignObj)
   if not alignObj:
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

   delta = subPoint(refObj[refHandle],alignObj[alignHandle])
   delta = addPoint(delta,[xSep,ySep])
   print "Align: " + str(delta)
 
   rodTranslate(alignObj,delta)
   refObj['_slaves'].append(alignObj)

def leftEdge(rod):
   return rod['lL'][0]

def topEdge(rod):
   return rod['uR'][1]

def bottomEdge(rod):
   return rod['lR'][1]

def rightEdge(rod):
   return rod['lR'][0]

def addPoint(a,b):
  return [a[0]+b[0],a[1]+b[1]]

def subPoint(a,b):
  return [a[0]-b[0],a[1]-b[1]]

def maxNinN(limit,obj,space):
   n = int(limit / (obj + space))
   #sometimes an extra can fit
   if n*space + (n+1)*obj <= limit:
      n += 1

   space = (limit - n * obj) / (n-1)
   return (n,space)

def rodFillBBoxWithRects(layer,fillBBox,width,length,spaceX,spaceY,gap="distribute",cvId=None):
   print "filBbox"
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

   return createObj(origin,bwidth,blength,rects)

def createObj(origin,twidth,tlength,subs=None):
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
            '_slaves' : []} 
   return obj

def rodCreatePath(layer,width,pts,termIOType,termName,pin,subRect=None,name=""):
  subs = []
  print "createPath: " + str(pts) + ", layer: " + str(layer) + ", sub: " + str(subRect)
  r = None
  if (layer[0],layer[1]) in layermap:
      l1 = layermap[ (layer[0],layer[1]) ]
      l1 = layout.layer(l1[0], l1[1])
      dpts = []
      for p in pts:
        dpts.append(db.DPoint.new(p[0],p[1]))  
      r = db.DPath.new(dpts,width)
      r = top.shapes(l1).insert(r)
      subs.append(r)

  bbox = r.dbbox()
  origin = [bbox.p1.x,bbox.p1.y]
  twidth = bbox.width()
  tlength = bbox.height()

  assert(len(pts) == 2)

  if subRect:
    assert(env['distributeSingleSubRect'])
    assert(len(subRect)==1)
    for s in subRect:
       n,space = maxNinN(twidth+s['beginOffset']+s['endOffset'],width,s['space'])
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


  obj = createObj(origin,twidth,tlength,subs)

  print "Path: " + str(obj)
  rodsByName[name] = obj
  return obj

def rodAddPoints(a,b):
   return [a[0]+b[0],a[1] + b[1]]

def rodAddToY(a,b):
   return [a[0],a[1] + b]

def rodAddToX(a,b):
   return [a[0]+b,a[1]]

def rodAssignHandleToParameter(**kwargs):
   print "assignHandle: " + str(kwargs)
   return None

def rodGetObj(i):
   print "rodGetObject: " + str(i)
   if i in rodsByName:
      return rodsByName[i]
   return None

def rodPointX(l):
   return l[0]

def rodPointY(l):
   return l[1]

def snapToGrid(v,g):
   ret = round(v/float(g))*g
   return ret

#dbCreateLabel(cv 4 1:1 "myLabel" "centerLeft" "R0" "roman" 2)
def dbCreateLabel(cell,layer,origin,text,justification,orientation,font,height):
   l1 = layermap[ (layer[0],layer[1]) ]
   l1 = layout.layer(l1[0], l1[1]) 
   t = db.DText.new(text,origin[0],origin[1])
   t.size = height
   t.halign = 1 #center
   t.valign = 1 #center
   top.shapes(l1).insert(t)
   print "createLabel: " + str([locals()[arg] for arg in inspect.getargspec(dbCreateLabel).args])

def dbCreateRect(cell,layer,coord):
   print "createRect2: " + str(layer) + ", " + str(coord)
   return rodCreateRect(layer,coord[1][0] - coord[0][0],coord[1][1] - coord[0][1],coord[0])

def get_pname(s):
   print "get_pname: " + str(s)
   return s

env = {}
def envSetVal(domain,key,t,v):
   env[key] = v

def concat(*args):
   ret = ""
   for a in args:
      ret += str(a)
   print "Concat: " + ret
   return ret

def rexMatchp(r,s):
   return re.match(r,s)

def nullfunc(*args):
   return None

def oddp(v):
   return v%2==1

def evenp(v):
   return v%2==0

def listp(v):
   return isinstance(v,list)

def isCallable(l):
   if not l.expr in skill.procedures:
      return False
   return not not skill.procedures[l.expr]

def cons(a,b):
   if isinstance(a,list):
     return a+b
   if isinstance(b,list):
     return [a] + b
   if not b:
     return [a]
   return [a,b]

def parseString(s,t):
   return s.split(t)

def strcat(*a):
   ret = ""
   for e in a:
     ret += e
   return ret

def nth(i,l): #TODO: not sure about this
   return l[int(i)]

def getLast(l):
   return l[-1]

def typep(v):
   if isinstance(v,float):
      return Lazy('flonum',evalstring)
   if isinstance(v,basestring):
      return Lazy('string',evalstring)
   if isinstance(v,list):
      return Lazy('list',evalstring)
   if isinstance(v,int):
      return Lazy('fixnum',evalstring)
   print type(v)
   assert(False) #TODO:

def eval(v):
   if isinstance(v,Lazy):
      return interp(v.expr)
   return v

def ddGetObjReadPath(o):
   return "."

def close(f):
   f.close()

def _gets(f):
   return f.readline()

def findFunc(name):
   def find(*args):
      print "********************" + name
      print args
      assert(False)
      exit(0)
   return find

######################End skill function impls

def write():
   layout.write("foo.gds")

layermap = {}
def run(props_file,layermap_file,s,r):
   global skill
   global interp
   global layermap
   global props
   global bag

   skill = s
   interp = r

   props = load_props(props_file)
   bag = props['props']


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
   skill.procedures['fixp'] = fixp
   skill.procedures['listp'] = listp
   skill.procedures['boundp'] = boundp
   skill.procedures['makeTable'] = makeTable
   skill.procedures['dbGet'] = dbGet
   skill.procedures['mod'] = mod
   skill.procedures['fix'] = fix
   skill.procedures['printf'] = printf
   skill.procedures['list'] = listl
   skill.procedures['car'] = car
   skill.procedures['xCoord'] = car
   skill.procedures['cadr'] = cadr
   skill.procedures['cdr'] = cdr
   skill.procedures['caddr'] = caddr
   skill.procedures['caadr'] = findFunc('caadr')
   skill.procedures['cadddr'] = cadddr
   skill.procedures['caar'] = findFunc('caar')
   skill.procedures['cadar'] = findFunc('cadar')
   skill.procedures['cadadr'] = findFunc('cadadr')
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
   skill.procedures['snapToGrid'] = snapToGrid
   skill.procedures['dbCreateLabel'] = dbCreateLabel
   skill.procedures['dbCreateRect'] = dbCreateRect 
   skill.procedures['dbCloseBag'] = nullfunc
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
   skill.procedures['rodCreatePolygon'] = findFunc('rodCreatePolygon')
   skill.procedures['get_pname'] = get_pname
   skill.procedures['concat'] = concat
   skill.procedures['rexMatchp'] = rexMatchp
   skill.procedures['oddp'] = oddp
   skill.procedures['evenp'] = evenp
   skill.procedures['isCallable'] = isCallable
   skill.procedures['dbSetq'] = nullfunc
   skill.procedures['cons'] = cons
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
   skill.procedures['getLast'] = getLast
   skill.procedures['length'] = len
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

