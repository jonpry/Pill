#!/usr/bin/python
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor, Node

grammar = r"""
     block      = ws? list
     list       = LPAR listelem* RPAR
     listelem   = (db/number/identifier/string/list) ws?

     db          = "db" COLON hex
     identifier  = ~"[a-zA-Z_][a-zA-Z_0-9]*" / ~r'\\[:,][0-9a-zA-Z]'
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

def load_props(file_name):
   g = Grammar(grammar)
   retd = {}
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
            retd[d['name']] = {'value': v}
            if'callback' in d:
               cbs[d['name']] = d['callback']
         continue
      t = ""
      if "valueType" in o:
        t = o["valueType"]
      if t == "float":
        o['value'] = float(o['value'])
      retd[o['name']] = o['value']
      if o['value'] == "valueType":
        print o
        print e
   return { 'props' : retd, 'cbs' : cbs}
     
#print load_props()
