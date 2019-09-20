#!/usr/bin/python

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


from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor, Node

grammar = r"""
     block      = ws? list
     list       = LPAR listelem* RPAR
     listelem   = (db/number/identifier/string/list) ws?

     db          = "db" COLON hex
     identifier  = ~"[a-zA-Z_][a-zA-Z_0-9]*" / ~r'\\[:,$][0-9a-zA-Z]'
     number      = float / integer / hex
     float       = ~'\d*\.\d*'
     hex         = "0x" ~'[0-9a-f]+'
     integer     = ~'\d+'
     string      = '"' ~r'\\.|[^\"\\]*'* '"'

     LPAR  = "(" ws?
     RPAR  = ")" ws?
     COLON = ":" 
     ws    = (~"\s+"/(";" ~r"[^\n]*"))+
     """

class Visitor(NodeVisitor):
   def __init__(self):
      self.unwrapped_exceptions = (Exception)
   
   def visit_ws(self,node,children):
      return None

   def visit_block(self,node,children):
      return children[1]
 
   def visit_list(self,node,children):
      return children[1]

   def visit_listelem(self,node,children):
      return children[0]

   def visit_identifier(self,node,children):
      return node.text

   def visit_nil(self,node,children):
      return None

   def visit_integer(self,node,children):
      return int(node.text)
    
   def visit_float(self,node,children):
      return float(node.text)

   def visit_string(self,node,children):
      return node.text[1:][:-1]

   def visit_db(self,node,children):
      return "db"

   def generic_visit(self,node,children):
        if node and "".join(node.text.split()) == "":
           return None
        ret = []
        for e in children:
           if e != None:
             ret.append(e)
        if len(ret)==0:
           return None
        if len(ret)==1:
           return ret[0]
        return ret

def toDict(e,skip):
   o = {}
   name=0
   for i in range(skip,len(e)):
      if i%2==skip%2:
        name=e[i]
      else:
        o[name] = e[i]
   return o

class ListProperty(list):
   def __init__(self,name,value):
       self.name = name
       super(ListProperty,self).__init__(self)
       for l in value:
          self.append(l)

   def __contains__(self,key):
       return key == "value" or key == "valueType" or key == "name"

   def __getitem__(self,key):
       if key == "value":
          return self
       elif key == "valueType":
          return "ILList"
       elif key == "name":
          return self.name
       return super(ListProperty,self).__getitem__(key)

  # create proxies for wrapped object's double-underscore attributes
class PropMetaBool(type):
   def __init__(cls, name, bases, dct):
      def make_proxy(name):
         def proxy(self, *args):
            return getattr(self.wrapped, name)
         return proxy

      type.__init__(cls, name, bases, dct)
      ignore = set("__%s__" % n for n in cls.__ignore__.split())
      for name in dir(bool):
         if name.startswith("__"):
            if name not in ignore and name not in dct:
               print(name)
               setattr(cls, name, property(make_proxy(name)))

class PropMetaStr(type):
   def __init__(cls, name, bases, dct):
      def make_proxy(name):
         def proxy(self, *args):
            return getattr(self.wrapped, name)
         return proxy

      type.__init__(cls, name, bases, dct)
      ignore = set("__%s__" % n for n in cls.__ignore__.split())
      for name in dir(str):
         if name.startswith("__"):
            if name not in ignore and name not in dct:
               print(name)
               setattr(cls, name, property(make_proxy(name)))


class BooleanProperty(int,metaclass=PropMetaBool):
   __ignore__ = "class mro new init setattr getattr getattribute getitem hash eq"
   def __new__(cls,name,value):
       if value == "nil":
          value = False
       return super(BooleanProperty,cls).__new__(cls,bool(value))

   def __init__(self,name,value):
       if value == "nil":
          value = False
       self.name = name
       self.wrapped = int(bool(value))

   def __contains__(self,key):
       return key == "value" or key == "valueType" or key == "name"

   def __eq__(self,b):
       #TODO: there are more cases of odd coercions to do here. such as "TRUE" and "FALSE"
       if not b or b == "nil":
          return self.wrapped == 0
       return self.wrapped == 1

   def __getitem__(self,key):
       if key == "value":
          return self
       elif key == "valueType":
          return "boolean"
       elif key == "name":
          return self.name
       assert(False) 

   def __setitem__(self,key,value):
       assert(key == "value")
       self.wrapped = value

class FloatProperty(float):
   def __new__(cls,name,value):
       return super(FloatProperty,cls).__new__(cls,value)
   def __init__(self,name,value):
       self.name = name

   def __contains__(self,key):
       return key == "value" or key == "valueType" or key == "name"
          
   def __getitem__(self,key):
       if key == "value":
          return self
       elif key == "valueType":
          return "float"
       elif key == "name":
          return self.name
       print(key)
       assert(False) 

class IntProperty(int):
   def __new__(cls,name,value):
       return super(IntProperty,cls).__new__(cls,value)
   def __init__(self,name,value):
       self.name = name

   def __contains__(self,key):
       return key == "value" or key == "valueType" or key == "name"

   def __getitem__(self,key):
       if key == "value":
          return self
       elif key == "valueType":
          return "int"
       elif key == "name":
          return self.name
       assert(False) 

class StringProperty(str,metaclass=PropMetaStr):
   __ignore__ = "class mro new init setattr getattr getattribute getitem hash eq"

   def __new__(cls,name,value):
       return super(StringProperty,cls).__new__(cls,value)

   def __init__(self,name,value):
       self.name = name
       self.wrapped = value;

   def __contains__(self,key):
       return key == "value" or key == "valueType" or key == "name"

   def __hash__(self):
       return self.wrapped.__hash__()

   def __eq__(self,b):
       return self.wrapped == b

   def __getitem__(self,key):
       if key == "value":
          return self
       elif key == "valueType":
          return "string"
       elif key == "name":
          return self.name
       print(self.wrapped)
       return self.wrapped.__getitem__(key)

   def __setitem__(self,key,value):
       assert(key == "value")
       self.wrapped = value


def Property(name,value,t):

    if t == "boolean":
       return BooleanProperty(name,value)
    if t == "string":
       return StringProperty(name,value)
    if t == "float":
       return FloatProperty(name,value)
    if t == "int":
       return IntProperty(name,value)
    if t == "ILList":
       return ListProperty(name,value)

    if t == "cyclic" or t == "radio":
       return StringProperty(name,value)

    print("t: " + t)
    assert(False)

class PropertyDict(dict):
   def __init__(self, *args):
      dict.__init__(self, args)

   def __setitem__(self, key, val):
      #assert(isinstance(val,StringProperty) or isinstance(val,BooleanProperty)
      #       or isinstance(val,FloatProperty) or isinstance(val,IntProperty))
      dict.__setitem__(self, key, val)

def load_props(file_name):
   g = Grammar(grammar)
   retd = PropertyDict()
   cbs = {}
   g = g.parse(open(file_name).read())
   iv = Visitor()
   l = iv.visit(g)
   for e in l:
      o = toDict(e,1)

      if o['name'] == "cdfData":
         o = toDict(o['value'],0)['parameters']
         for p in o:
            d = toDict(p,0)
            v = d['defValue']
            if v.startswith("iPar"):
               v = "1" #TODO: hack
            if d['type'] == "boolean":
               v = True if v == 't' else None
            retd[d['name']] = Property(d['name'],v,d['type'])
            if'callback' in d:
               cbs[d['name']] = d['callback']
         continue
      t = ""
      if "valueType" in o:
        t = o["valueType"]
      if t == "float":
        o['value'] = float(o['value'])
      retd[o['name']] = Property(o['name'],o['value'],t)
      if o['value'] == "valueType":
        print(o)
        print(e)
   return { 'props' : retd, 'cbs' : cbs}
     
#print load_props()
