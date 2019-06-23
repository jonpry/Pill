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

import re
import numpy as np
import compiler
import sys
import types
import dis
import compiler
import pdb
import new
import inspect
import traceback
import peak
import bisect
import tools
import hashlib
import marshal
import copyreg
import pickle
import context
from tools import Lazy
from tools import SkillList
from types import FunctionType
from functools import wraps
from parsimonious.grammar import Grammar, Literal
from parsimonious.nodes import NodeVisitor, Node
from assembler.assembler import Code, Compare, dump, Pass
from dis import dis

sys.setrecursionlimit(100*1000)

def flatten(items):
    for x in items:
        print x
        if (hasattr(x, '__iter__') or hasattr(x, '__getitem__')) and not isinstance(x, (str, bytes)):
            print "it"
            for sub_x in flatten(x):
                yield sub_x
        else:
            yield x

grammar = r"""
     block       = ws? stmts
     procedure   = PROCEDURE LPAR ws? identifier LPAR ws? (identifier ws?)* string? ws? RPAR ws? stmts RPAR
     identifier  = !((reserved) (ws/RPAR/EQU/PLUS/MINUS/RBR/BANG/TILDA/LT/GT/DOT/LPAR)) ~"[a-zA-Z_][a-zA-Z_0-9]*"
     reserved    = IF / ELSE / THEN / FOR / PROCEDURE / WHEN / LET / UNLESS / CASE / NIL / FOREACH / SETOF / EXISTS / TAU / RETURN / COND / WHILE 
     list        = LPAR (listelem ws?)* RPAR
     keyword_func= LPAR func_name ws? ((Q identifier ws?)? ororexpr ws?)+ RPAR
     func_call2  = func_name LPAR ws? ((Q identifier ws?)? ororexpr ws?)+ RPAR
 
     func_name   = "fixp" / "bar" / "bam"
     listelem    = assign/list  
     ifthen      = THEN ws? stmts ws? (ELSE ws? stmts?)?
     ifstmt      = stmt (ws? stmt)?
     if          = IF LPAR ws? assign ws?  (ifthen/ifstmt) ws? RPAR
     while       = WHILE LPAR ws? assign ws? stmts RPAR
     when        = WHEN LPAR ws? assign ws? stmts RPAR
     unless      = UNLESS LPAR ws? assign ws? stmts RPAR
     case        = CASE LPAR identifier ws? case_list RPAR
     exists      = EXISTS LPAR identifier ws? ororexpr ws? assign RPAR
     foreach     = FOREACH LPAR identifier ws? assign ws? stmts RPAR
     for         = FOR LPAR identifier ws? assign ws? assign ws? stmts RPAR
     cond        = COND LPAR (LPAR assign ws? stmts ws? RPAR)+ RPAR
     case_list   = LPAR (list / assign) ws? stmts ws? RPAR case_list?
     proglet     = (PROG/LET) LPAR ((LPAR (identifier ws?)* RPAR)/NIL) stmts ws? RPAR
     return      = RETURN (LPAR assign? RPAR)?
     number      = ~'\d+\.?\d*' ~"[u]|e-?[0-9]+"?
     string      = '"' ~r'\\.|[^\"\\]*'* '"'
     stmt        = procedure / proglet / if / case / when / unless / while / foreach / for / return / assign / cond / exists /list
     stmts       = stmt ws? stmts?
      

     value      = (keyword_func/func_call2/if/exists/identifier/number/string/NIL/TAU) ws?

 
     vexpr      = (LPAR assign RPAR) / value
     aryexpr    = vexpr ws? (LBR assign RBR)?
     bitexpr    = aryexpr ws? ( LT assign GT )?
     rangeexpr  = bitexpr ws? ( LT assign COLON assign GT)?
     quoteexpr  = (PRIME (list/rangeexpr)) / rangeexpr
     dotexpr    = DOT? quoteexpr
     getrefexpr = dotexpr (DOT dotexpr)*
     derefexpr  = getrefexpr (ARROW getrefexpr)*
     lderefexpr = derefexpr (SARROW derefexpr)*
     princexpr = INC? lderefexpr
     poincexpr = princexpr INC?
     prdecexpr = DEC? poincexpr
     podecexpr = prdecexpr DEC?
     negexpr   = MINUS? podecexpr
     notexpr   = BANG? negexpr
     bnotexpr  = TILDA? notexpr 
     expexpr  = bnotexpr (EXP bnotexpr)*
     mulexpr  = expexpr  (STAR expexpr)*
     divexpr  = mulexpr  (DIV mulexpr)*
     plusexpr = divexpr  (PLUS divexpr)*
     diffexpr = plusexpr (MINUS plusexpr)*
     lsexpr   = diffexpr (LEFT diffexpr)*
     rsexpr   = lsexpr (RIGHT lsexpr)*
     ltexpr   = rsexpr (LT rsexpr)*
     gtexpr   = ltexpr (GT ltexpr)*
     leexpr   = gtexpr (LE gtexpr)*
     geexpr   = leexpr (GE leexpr)*
     eqexpr   = geexpr (EQUEQU geexpr)*
     neqexpr  = eqexpr    (BANGEQU eqexpr)*
     bandexpr = neqexpr   (AND neqexpr)*
     bnandexpr= bandexpr  (NAND bandexpr)*
     bxorexpr = bnandexpr (HAT bnandexpr)*
     bxnorexpr = bxorexpr (XNOR bxorexpr)*
     borexpr  = bxnorexpr (OR bxnorexpr)*
     bnorexpr = borexpr (NOR borexpr)*
     andandexpr  = bnorexpr (ANDAND andandexpr)?
     ororexpr   = andandexpr (OROR ororexpr)?
     tuple       = ororexpr (ws? COLON ororexpr ws?)?
     assign     = tuple (EQU assign)?


     TAU = "t" ws?
     IF = "if"
     ELSE = "else"
     THEN = "then"
     FOR = "for"
     PROCEDURE = "procedure"
     WHEN = "when"
     LET = "let"
     UNLESS = "unless"
     CASE = "case"
     PROG = "prog"
     NIL = "nil"
     FOREACH = "foreach"
     SETOF = "setof"
     EXISTS = "exists"
     RETURN = "return"
     COND = "cond"
     WHILE = "while"

     LPAR        = "(" ws?
     RPAR        = ")" ws?
     STAR  = "*" ws?
     DIV   = "/" ws?
     MOD   = "%" ws?
     PLUS  = "+" ws?
     MINUS = "-" ws?
     LEFT  = "<<" ws?
     RIGHT = ">>" ws?
     LE    = "<=" ws?
     GE    = ">=" ws?
     LT    = "<" ws?
     GT    = ">" ws?
     EQUEQU = "==" ws?
     BANGEQU = "!=" ws?
     NAND  = "~&" ws?
     XNOR  = "~^" ws?
     NOR   = "~|" ws?
     AND   = "&" ws?
     OR    = "|" ws?
     ANDAND = "&&" ws?
     OROR   = "||" ws?
     INC    = "++" ws?
     DEC    = "--" ws?
     TILDA  = "~" ws?
     BANG  = "!" ws?
     HAT   = "^" ws?
     EQU   = "=" ws?
     LBR   = "[" ws?
     RBR   = "]" ws?
     EXP   = "**" ws?
     COLON = ":" ws?
     PRIME = "'"
     Q     = "?"
     ARROW = "->"
     SARROW = "~>" ws?
     DOT   = "."
     ws    = (~"\s+"/(";" ~r"[^\n]*"))+
     """

verbose_visit=False
class Visitor(NodeVisitor):
    def __init__(self,breaks,useSkl):
        self.c = Code()
        self.c.co_argcount = 0
        self.c.co_varnames = []
        self.c.co_firstlineno = 1
        self.code_stack = [self.c]
        self.locals = []
        self.returns = []
        self.blocks = 0
        self.useSkl = useSkl
        self.breaks = breaks
        self.unwrapped_exceptions = (Exception)

        comps = { "eqexpr" : "==", "neqexpr" : "!=", "ltexpr" : "<", "leexpr" : "<=", "gtexpr" : ">", "geexpr" : ">="}
        for k,v in comps.iteritems():
           setattr(self, "visit_" + k, types.MethodType(lambda self, node, children, v=v: self.compexpr(node,children,v), self, Visitor))
      
        binary = { "bandexpr" : [Code.BINARY_AND],      "plusexpr" : [Code.BINARY_ADD], "diffexpr" : [Code.BINARY_SUBTRACT],
                   "borexpr"  : [Code.BINARY_OR],       "bxorexpr" : [Code.BINARY_XOR],  "divexpr" : [Code.BINARY_DIVIDE], 
                   "mulexpr"  : [Code.BINARY_MULTIPLY],  "expexpr" : [Code.BINARY_POWER], "rsexpr" : [Code.BINARY_RSHIFT],
                   "lsexpr"   : [Code.BINARY_LSHIFT],
                   "bnorexpr" : [Code.BINARY_OR, Code.UNARY_INVERT],
                   "bnandexpr": [Code.BINARY_AND, Code.UNARY_INVERT],
                   "bxnorexpr": [Code.BINARY_XOR, Code.UNARY_INVERT],
                   "getrefexpr"   : [Code.BINARY_LSHIFT],} #TODO: not implemented
        for k,v in binary.iteritems():
           setattr(self, "visit_" + k, types.MethodType(lambda self, node, children, v=v: self.binexpr(node,children,v), self, Visitor))
      
        unary = { "negexpr" : [0,Code.UNARY_NEGATIVE,False], "bnotexpr" : [0,Code.UNARY_INVERT,False], "notexpr" : [0,Code.UNARY_NOT,True],
                  "dotexpr" : [0,Code.UNARY_NEGATIVE,False]}

        for k,v in unary.iteritems():
           setattr(self, "visit_" + k, types.MethodType(lambda self, node, children, v=v: self.unaexpr(node,children,v), self, Visitor))

        incdec = {"podecexpr" : [1,-1], "prdecexpr" : [0,-1], #TODO inc/dec not implemented yet
                  "poincexpr" : [1,+1], "princexpr" : [0,+1]}

        for k,v in incdec.iteritems():
           setattr(self, "visit_" + k, types.MethodType(lambda self, node, children, v=v: self.incexpr(node,children,v), self, Visitor))

        logical = { "ororexpr" : [Code.POP_JUMP_IF_TRUE, True], "andandexpr" : [Code.POP_JUMP_IF_FALSE, False]}
        for k,v in logical.iteritems():
           setattr(self, "visit_" + k, types.MethodType(lambda self, node, children, v=v: self.logicexpr(node,children,v), self, Visitor))

        nulls = ["rangeexpr", "bitexpr", "listelem"]
        for k in nulls:
           setattr(self, "visit_" + k, types.MethodType(lambda self, node, children, v=v: self.nullexpr(node,children,v), self, Visitor))

    def compexpr(self, node, children, op):
       def gen(ref=False,children=children,op=op):
          children[0](ref=ref)
          #print node.expr_name
          if children[1]:
             #dump(self.c.code())
             ps = self.c.stack_size
             for e in children[1]:
                e[1]()
                self.c.COMPARE_OP(op)
             assert(ps == self.c.stack_size and ref==False)
       return gen

    def binexpr(self, node, children, ops):
       def gen(ref=False,children=children,node=node,ops=ops):
          children[0](ref=ref)
          #is_sub=ops[0] == Code.BINARY_SUBTRACT
          #print node.expr_name
          if children[1]:
             ps = self.c.stack_size
             for e in children[1]:
                e[1]()
                #if is_sub:
                # self.pprint("B: ")
                for op in ops:
                   op(self.c)
             assert(ps == self.c.stack_size and ref==False)
       return gen

    def nullexpr(self, node, children, ops):
       def gen(ref=False,children=children,ops=ops):
          try:
             children[0](ref=ref)
          except Exception as e:
             print traceback.format_exc(e)
             print node.expr_name
             print node.text
             exit(0)

       return gen

    def unaexpr(self, node, children, op):
       def gen(ref=False,children=children,op=op,node=node):
          c = children[(op[0]+1)%2]
          if isinstance(c,list):
             print node.expr_name
             assert(False)
             exit(0)
          c(ref=ref)          
          if children[op[0]]:
             if op[2]:
               self.coerse()
             op[1](self.c)
       return gen

    def incexpr(self, node, children, op):
       def gen(ref=False,children=children,op=op,node=node):
          c = children[(op[0]+1)%2]
          if isinstance(c,list):
             print node.expr_name
             assert(False)
             exit(0)
          if not children[op[0]]:
             c(ref=ref)
             return    
          postinc = op[0] == 0
       
          c(ref=True)
          #obj,key
          self.c.DUP_TOP()
          #obj,key,key
          self.c.ROT_THREE()
          self.c.ROT_THREE()
          #key,key,obj
          self.c.DUP_TOP()
          #key,key,obj,obj
          self.c.ROT_THREE()
          self.c.ROT_THREE()
          #key,obj,obj,key
          self.c.BINARY_SUBSCR()
          #key,obj,value
          self.c.DUP_TOP()
          #key,obj,value,value
          self.c.LOAD_CONST(op[1])
          self.c.BINARY_ADD()
          #key,obj,value,newvalue
          if postinc:
             self.c.ROT_TWO()
             self.c.POP_TOP()
             #key,obj,newvalue
             self.c.DUP_TOP()
             self.c.ROT_FOUR()
             #newvalue,key,obj,newvalue
          else:
             self.c.ROT_TWO()
             #key,obj,newvalue,value
             self.c.ROT_FOUR()
             #value,key,obj,newvalue

          self.c.ROT_THREE()
          #newvalue,newvalue,key,obj
          self.c.ROT_TWO()
          #newvalue,newvalue,obj,key
          self.c.STORE_SUBSCR()

       return gen

    def visit_quoteexpr(self,node,children):
       #quoteexpr  = (PRIME (list/rangeexpr)) / rangeexpr 
       def gen(ref=False,children=children,node=node):
          if not isinstance(children[0],list):
            return children[0](ref=ref)

          self.c.LOAD_GLOBAL('Lazy')
          self.c.LOAD_CONST(node.text[1:])
          self.c.LOAD_GLOBAL('runtime')
          self.c.LOAD_ATTR('evalstring')
          self.c.CALL_FUNCTION(2,0)
       return gen

    def logicexpr(self, node, children, op):
       #print "parse"
       #print children
       def gen(ref=False,children=children,op=op):
          #print "gen"
          #print children
          children[0](ref=ref)

          if not children[1]:
            return

          self.coerse()
 
          ps = self.c.stack_size
          p2 = op[0](self.c)
          children[1][0][1]()
          self.coerse()
          p1 = op[0](self.c)
          self.c.LOAD_CONST(None if op[1] else True)
          done = self.c.JUMP_ABSOLUTE()
          p2()
          p1()
          self.c.LOAD_CONST(None if not op[1] else True)
          done()
          assert(ps == self.c.stack_size and ref==False)
       return gen

    #This interprets boolean according to skill 
    #TODO empty list is treated as false
    def coerse(self):
       self.c.DUP_TOP()
       self.c.LOAD_CONST(None)
       self.c.COMPARE_OP("==")
       not_done = self.c.POP_JUMP_IF_FALSE()
       self.c.POP_TOP()
       self.c.LOAD_CONST(False) 
       done1 = self.c.JUMP_FORWARD()
       not_done()
       self.c.DUP_TOP()
       self.c.LOAD_GLOBAL("isinstance")
       self.c.ROT_TWO()
       self.c.LOAD_GLOBAL("bool")
       self.c.CALL_FUNCTION(2)
       not_done = self.c.POP_JUMP_IF_FALSE()
       done2 = self.c.JUMP_FORWARD()
       not_done()
       #self.c.DUP_TOP()
       #self.c.LOAD_CONST("hasattr")
       #self.c.ROT_TWO()
       #self.c.LOAD_CONST("__len__")
       #self.c.CALL_FUNCTION(2)
       #not_done = self.c.POP_JUMP_IF_FALSE()
       #self.c.LOAD_ATTR("__len__")
       #empty_list = self.c.POP_JUMP_IF_FALSE()
       #self.c.LOAD_CONST(True)
       #done3 = self.c.JUMP_FORWARD()
       #self.c.LOAD_CONST(False)
       #done4 = self.c.JUMP_FORWARD()
       #not_done()
       self.c.POP_TOP()
       self.c.LOAD_CONST(True)
       done1()
       done2()
       #done3()
       #done4()
    def visit_derefexpr(self,node,children):
       def gen(ref=False,node=node,children=children):
          self.do_deref(ref,node,children)
       return gen

    #TODO: this does not actually work if item is a list
    def visit_lderefexpr(self,node,children):
       def gen(ref=False,children=children,node=node):
          self.do_deref(ref,node,children)
       return gen

    def do_deref(self,ref,node,children):
          #self.pprint("Dict: ")
          if children[1]:
             #self.c.LOAD_CONST(self.c.stack_size)
             #self.pprint("Stack at lderef enter: ")
             #self.c.POP_TOP()

             lde1 = self.c.stack_size
             #pdb.set_trace()
             children[0](ref=True)
             lde2 = self.c.stack_size
             #print node.text + ", Was: " + str(ref) 
             if lde2 - lde1 == 2:
                self.c.BINARY_SUBSCR()
             #stack: obj
             #self.c.LOAD_CONST(self.c.stack_size)
             #self.pprint("Stack at lderef left: ")
             #self.c.POP_TOP()

             for i in range(len(children[1])):
                #self.pprint("Tos4: ")
                #self.c.LOAD_CONST(self.c.stack_size)
                #self.pprint("Stack at lderef get: ")
                #self.c.POP_TOP()
                e = children[1][i]
                #stack is object
                e[1](ref=True)  
                #self.c.LOAD_CONST(self.c.stack_size)
                #self.pprint("Stack at lderef getdone: ")
                #self.c.POP_TOP()
                #stack : object, #vars, label
                self.c.ROT_TWO()
                #stack : object, label, #vars
                self.c.POP_TOP()
                #stack : object, label
                self.c.ROT_TWO()
                #self.pprint("Obj: ")
                self.c.ROT_TWO()
                #self.pprint("Idx: ")
                self.c.LOAD_CONST(ref)
                #self.pprint("Ref: ")
                self.c.POP_TOP()
                if i == len(children[1])-1 and ref:
                   pass
                else: 
                   self.c.BINARY_SUBSCR()
                #stack new object
          else:
             children[0](ref=ref)

    def visit_aryexpr(self,node,children):
       #aryexpr    = vexpr ws? (LBR ororexpr RBR)?
       def gen(ref=False,node=node,children=children):
          if children[2]:
             children[0](ref=False)
             children[2][0][1]()
             #print ref
             if not ref:
                self.c.BINARY_SUBSCR()
          else:
             children[0](ref=ref)
       return gen

    def visit_vexpr(self,node,children):
       def gen(ref=False,node=node,children=children):
          if hasattr(children[0],"__len__"):
             children[0][1](ref=ref)
             return
          children[0](ref=ref)
       #print "v: " + str(gen)
       return gen

    def visit_tuple(self,node,children):
       #tuple       = ororexpr (ws? COLON ororexpr ws?)?
       def gen(ref=False,node=node,children=children):
          children[0](ref=ref)
          if children[1]:       
             children[1][0][2](ref=ref)
             self.c.BUILD_LIST(2)

       return gen

    def do_return(self):
       #for i in range(self.blocks):
       #   self.c.POP_BLOCK()
       #TODO: pop block doesn't work here because of strange bytecodeassembler behavior, not sure if interpreter cares

       for i in range(self.c.stack_size-1):
          self.c.ROT_TWO()
          self.c.POP_TOP()
       self.returns.append(self.c.JUMP_ABSOLUTE())


    def visit_return(self,node,children):
       #return      = RETURN (LPAR assign? RPAR)?
        def gen(node=node,children=children):
           #print "return: " + str(self.c.stack_size)
           if children[1] and children[1][0][1]:
              children[1][0][1][0]()
           else:
              self.c.LOAD_CONST(None)
           self.do_return()
        return gen

    def visit_number(self, node, children):
       def gen(ref=False,node=node):
          v = float(children[0].text)
          if children[1]:
             #print "suffix"
             t = children[1][0].text
             if t == "u":
                v *= 1e-6
             elif t[0] == "e":
                m = children[0].text
                m+=t
                v = float(m)
             else:
                print t
                assert(False)
                exit(0)
          else:
             try:
                v = int(children[0].text)
             except:
                pass
          self.c.LOAD_CONST(v)
       return gen

    def visit_string(self, node, children):
       def gen(ref=False,node=node):
          t = node.text[1:][:-1]
          t = t.decode('string_escape')
          self.c.LOAD_CONST(t)
       return gen

    def visit_identifier(self,node,children):
       def gen(ref=False,children=children):
          return ("identifier",children[1].text)
       return gen

    def visit_func_name(self,node,children):
       def gen(ref=False,children=children):
          return ("identifier",children[0].text)
       return gen

    def visit_keywordfunc(self,node,children):
       def gen(ref=False,children=children):
          #print keywordfunc()
          self.c.LOAD_CONST(-4) #TODO
       return gen

    #keyword_func= LPAR func_name ws? ((Q identifier ws?)? ororexpr ws?)+ RPAR
    def kwfunc(self,ident,node,children):
       def gen(ref=False,ident=ident,node=node,children=children):
          self.c.set_lineno(bisect.bisect_left(self.breaks,node.start))
 
          ps = self.c.stack_size

          self.c.LOAD_FAST('#procs')
          self.c.LOAD_CONST(children[ident]()[1])
          self.c.BINARY_SUBSCR()
          keywords = []
          positional = []

          for e in children[3]:
             if e[0]:
                keywords.append((e[0][0][1]()[1],e[1]))
             else:
                positional.append(e[1])

          for e in positional:
             e()

          for k,v in keywords:
             self.c.LOAD_CONST(k)
             v()

          assert(self.c.stack_size == ps + 1 + len(positional) + len(keywords)*2)

          self.c.CALL_FUNCTION(len(positional),len(keywords)) 

          assert(ps+1 == self.c.stack_size)

       return gen

    def visit_keyword_func(self,node,children):
       return self.kwfunc(1,node,children)

    def visit_func_call2(self,node,children):
       #func_call2  = identifier LPAR ws? (Q identifier ws? (ororexpr/list) ws?)+ RPAR
       return self.kwfunc(0,node,children)

    def visit_proglet(self,node,children):
       # PROG LPAR LPAR (identifier ws?)* RPAR stmts ws? RPAR
       # (PROG/LET) LPAR ((LPAR (identifier ws?)* RPAR)/NIL) stmts ws? RPAR

       def gen(ref=False,node=node,children=children):
          self.locals.append([])

          for e in children[2]:
             self.locals[-1].append(e[0]()[1])

          #init and push var
          self.c.LOAD_GLOBAL('PushVars')
          for e in self.locals[-1]:
             self.c.LOAD_CONST(e)
          self.c.BUILD_LIST(len(self.locals[-1]))
          self.c.CALL_FUNCTION(1)
          self.c.POP_TOP()  

          #print "l: " + str(len(self.locals[-1]))
          #print self.c.stack_size

          self.c.LOAD_CONST(None) #Nil is default return value
          children[3]()
          #TODO: returns should point here but need a stack of stack target sizes first 
          #restore var
          self.c.LOAD_GLOBAL('PopVars')
          for e in self.locals[-1]:
             self.c.LOAD_CONST(e)
          self.c.BUILD_LIST(len(self.locals[-1]))
          self.c.CALL_FUNCTION(1)
          self.c.POP_TOP()
          self.locals = self.locals[:-1] 
       return gen

    def visit_let(self,node,children):
       # LET LPAR (identifier ws?)* stmts RPAR
       def gen(ref=False,node=node,children=children):
          self.c.LOAD_CONST(None)
          children[3]()
       return gen

    def visit_list(self,node,children):
       def gen(ref=False,node=node,children=children):
           if not children[1]:
                #self.c.LOAD_GLOBAL('SkillList')
                self.c.BUILD_LIST(0)
                #self.c.CALL_FUNCTION(1,0)
           else:
             cnt=0
             if len(children[1]) == 1:
                if self.useSkl:
                   self.c.LOAD_GLOBAL('SkillList')
                children[1][0][0](ref=ref)
                self.c.BUILD_LIST(1)
                if self.useSkl:
                   self.c.CALL_FUNCTION(1)
                return


             for e in children[1]:
                e[0]()
                if cnt==0:
                   self.c.DUP_TOP()
                else:
                   self.c.ROT_TWO()
                cnt+=1 
             
             self.c.POP_TOP()
             self.c.BUILD_LIST(cnt)

             #TODO collapse list of one item
 
             #dump(self.c.code())
             #print "list"
             #exit(0)
       return gen

    def visit_value(self, node, children):
        def gen(ref=False,node=node,children=children):
           #print children
           self.c.set_lineno(bisect.bisect_left(self.breaks,node.start))

           if "".join(node.text.split()) == "t":
              self.c.LOAD_CONST(True)
              return

           if "".join(node.text.split()) == "nil":
              self.c.LOAD_CONST(None)
              return

           if not callable(children[0][0]):
              print node.text
              assert(False)
              exit(0)
           r = children[0][0](ref=ref)
           if r:
              #print "ss1: " + str(self.c.stack_size)

              #print r[1]
              self.c.LOAD_FAST('#vars')
              self.c.LOAD_CONST(r[1])
              #print "ss2: " + str(self.c.stack_size)

              if not ref:
                 self.c.BINARY_SUBSCR()

              #self.pprint("Ret: ")


        return gen

    def visit_while(self,node,children):
       #WHEN LPAR ws? ororexpr ws? stmts RPAR
       def gen(ref=False,node=node,children=children):
          self.gen_cond(node,children[3],children[5],None,True)
       return gen

    def visit_when(self,node,children):
       #WHEN LPAR ws? ororexpr ws? stmts RPAR
       def gen(ref=False,node=node,children=children):
          self.gen_cond(node,children[3],children[5],None)
       return gen

    def visit_unless(self,node,children):
       #WHEN LPAR ws? ororexpr ws? stmts RPAR
       def gen(ref=False,node=node,children=children):
          self.gen_cond(node,children[3],None,children[5])
       return gen
  
    def gen_cond(self,node,cond,th_code,el_code,loop=False):
        self.c.LOAD_CONST(None)
        ps = self.c.stack_size
        if loop:
           tgt = self.c.here()
        cond()
        self.coerse()
        els = self.c.POP_JUMP_IF_FALSE()     
        #if code
        th_code()
        done = None           
        try:
           if loop:
              self.c.JUMP_ABSOLUTE(tgt)
           else:
              done = self.c.JUMP_ABSOLUTE()        
        except Exception as e:
           print str(e)
           print node.text
           print "dead code"
        els()
        #else code
        if el_code:
           el_code()
        if done:
           done()
        if(ps!=self.c.stack_size):
           print ps
           print self.c.stack_size
           print node.text
           assert(False)
           exit(0)

    def visit_cond(self,node,children):
       #COND LPAR (LPAR ororexpr ws? stmts ws? RPAR)+ RPAR
       def gen(node=node,children=children):
          for e in children[2]:
             self.gen_cond(node,e[1],e[3],None)
       return gen
 

  #ifthen      = THEN ws? stmts ws? (ELSE ws? stmts?)?
  #  ifstmt      = stmt (ws? stmt)?
    def visit_ifstmt(self,node,children):
       return (children[0],children[1][0][1] if children[1] else None)

    def visit_ifthen(self,node,children):
       return (children[2],children[4][0][2][0] if children[4] and children[4][0][2] else None)

    def visit_if(self,node,children):
        #if = IF LPAR ws? assign ws?  (ifthen/ifstmt) ws? RPAR
        def gen(ref=False,node=node,children=children):
           #print children[5]
           #exit(0)
           self.gen_cond(node,children[3],children[5][0][0],children[5][0][1])
        return gen

    def visit_case_list(self,node,children):
      #LPAR (list / assign) ws? stmts ws? RPAR case_list?
      if not children[6]:
         return ([children[1][0]],[children[3]])
      v,s = children[6][0]
      v = v + [children[1][0]]
      s = s + [children[3]]
      return (v,s)

    def visit_case(self,node,children):
      #CASE LPAR identifier ws? case_list RPAR
      def gen(ref=False,node=node,children=children):
         v = children[2]()[1]
         self.c.LOAD_FAST("#vars")
         self.c.LOAD_CONST(v)
         self.c.BINARY_SUBSCR()
         
         v,s = children[4]
         dones = []
         for i in range(len(v)):
            self.c.DUP_TOP()
            #input,input
            v[i]()
            #input,input,case
            self.c.DUP_TOP()
            #input,input,case,case
            self.c.ROT_THREE()
            #input,case,input,case
            self.c.COMPARE_OP("==")
            #input,case,comp
            run = self.c.POP_JUMP_IF_TRUE()
            self.c.DUP_TOP()
            #input,case,case
            self.c.LOAD_GLOBAL("isinstance")
            self.c.ROT_TWO()
            self.c.LOAD_GLOBAL("list")
            self.c.CALL_FUNCTION(2)
            #input,case,islist
            norun = self.c.POP_JUMP_IF_FALSE()
            #input,case
            self.c.ROT_TWO()
            #case,input
            self.c.DUP_TOP()
            #case,input,input
            self.c.ROT_THREE()
            #input,case,input
            self.c.ROT_TWO()
            #input,input,case
            self.c.COMPARE_OP("in")
            #input,in
            norun2 = self.c.POP_JUMP_IF_FALSE()
            self.c.LOAD_CONST(None)
            #input,none
            #self.c.JUMP_ABSOLUTE(run)
            
            run()
            self.c.POP_TOP()
            self.c.LOAD_CONST(None)
            s[i]()
            self.c.ROT_TWO()
            self.c.POP_TOP()
            dones.append(self.c.JUMP_FORWARD())
            norun()
            self.c.POP_TOP()
            norun2()

         for d in dones:
            d()
      return gen

    def visit_exists(self,node,children):
       #EXISTS LPAR identifier ws? ororexpr ws? assign RPAR
       def gen(ref=False,node=node,children=children):
          def pred(node=node,children=children):
             self.c.POP_TOP()
             self.pprint("v: ")
             children[6]()
             self.c.DUP_TOP()
             self.coerse()
             fwd = self.c.POP_JUMP_IF_FALSE()
             self.c.BUILD_LIST(1)
             self.pprint("pred: ")
             ret=self.c.JUMP_FORWARD()   
             fwd()
             self.c.POP_TOP()
             self.c.LOAD_CONST(None)
             return ret
          children[4]()
          self.pprint("Range: ")
          self.c.POP_TOP()
          self.gen_loop(children[2]()[1],children[4],pred,rtrue=False)
       return gen

    def visit_for(self,node,children):
       # FOR LPAR identifier ws? ororexpr ws? ororexpr ws? stmts RPAR
       def gen(node=node,children=children):
          def range_compute(node=node,children=children):
              self.c.LOAD_GLOBAL('range')
              self.c.LOAD_GLOBAL('int')
              children[4]() #get initial value
              self.c.CALL_FUNCTION(1)
              self.c.LOAD_GLOBAL('int')
              children[6]() #get end value
              self.c.CALL_FUNCTION(1)
              self.c.LOAD_CONST(1)
              self.c.BINARY_ADD()
              self.c.CALL_FUNCTION(2)
             
          self.gen_loop(children[2]()[1],range_compute,children[8])
       return gen

    def do_exit(self):
        self.c.LOAD_GLOBAL('exit')
        self.c.LOAD_CONST(0)
        self.c.CALL_FUNCTION(1)
        self.c.POP_TOP()

    def gen_loop(self,var,iter_obj,stmts,rtrue=True):
        #print "ss: " + str(self.c.stack_size)
        self.c.LOAD_GLOBAL('PushVars')
        self.c.LOAD_CONST(var)
        self.c.BUILD_LIST(1)
        self.c.CALL_FUNCTION(1,0)
        self.c.POP_TOP()


        iter_obj() #get initial value
        #self.pprint("Init: ")        

        self.c.GET_ITER()
        #self.pprint("IterObj: ")        

        loop = self.c.here()

        fwd = self.c.FOR_ITER()
        #self.pprint("Iter: ")        

        self.c.LOAD_FAST("#vars")
        self.c.LOAD_CONST(var)
        self.c.STORE_SUBSCR()
        self.c.LOAD_CONST(None)
        #do statements

        done = stmts() 

        self.c.POP_TOP()
        self.c.JUMP_ABSOLUTE(loop)
        fwd()
        fwd = self.c.JUMP_FORWARD()

        if done:
          done()
          self.c.ROT_THREE()
          self.c.POP_TOP()    
          self.c.POP_TOP()    

        fwd()

        self.c.LOAD_GLOBAL('PopVars')
        self.c.LOAD_CONST(var)
        self.c.BUILD_LIST(1)
        self.c.CALL_FUNCTION(1,0)    
        if rtrue:
           self.c.POP_TOP()    
           self.c.LOAD_CONST(True) #foralways returns true

    def visit_foreach(self,node,children):
       # FOREACH LPAR identifier ws? ororexpr ws? stmts RPAR
       def gen(node=node,children=children):
          self.gen_loop(children[2]()[1],children[4],children[6])
       return gen

    def visit_assign(self,node,children):
#       assign     = tuple (EQU assign)?
        def gen(ref=False,node=node,children=children):
            print not not children[1]
            if children[1]:
               #print "As: " + str(self.c.stack_size) 
               children[1][0][1]()  
               #stack: rhs
               self.c.DUP_TOP()
               #stack: rhs,rhs
               children[0](ref=True)
               #stack: rhs,rhs,obj,label
               self.c.STORE_SUBSCR()#TOS1[TOS] = TOS2.
               #print "Bs: " + str(self.c.stack_size) 
               #exit(0)
            else:
               children[0](ref=ref)
        return gen

    def visit_stmt(self,node,children):
        def gen(node=node,children=children):
            self.c.POP_TOP()
            return children[0]()
        return gen

    def visit_stmts(self,node,children):
        def gen(node=node,children=children):
           try:
              children[0]()
           except Exception as e:
              print str(e)
              print traceback.format_exc(e)
              print node.text
              print "possible dead code"
           if children[2]:
              children[2][0]()
        return gen

    def pprint(self,t):
       self.c.LOAD_CONST(t)
       self.c.PRINT_ITEM()
     
       self.c.DUP_TOP()
       self.c.PRINT_ITEM()
       self.c.PRINT_NEWLINE()

    def prolog(self):
       self.c.LOAD_GLOBAL('skill')
       self.c.LOAD_ATTR('procedures')
       self.c.STORE_FAST('#procs')

       self.c.LOAD_GLOBAL('skill')
       self.c.LOAD_ATTR('variables')
       self.c.STORE_FAST('#vars')


    def visit_procedure(self,node,children): 
        # PROCEDURE LPAR ws? identifier LPAR ws? (identifier ws?)* RPAR ws? stmts RPAR
        def gen():
           self.c = Code()
           self.code_stack.append(self.c)

           self.c.co_argcount = 0
           self.c.co_varnames = []
           self.c.co_firstlineno = 1

           proc = children[3]()[1]
           #print proc
           self.c.co_name = proc

           self.locals.append([])

           for e in children[6]:
              self.locals[-1].append(e[0]()[1])
              self.c.co_argcount += 1
              self.c.co_varnames.append(e[0]()[1])

           self.prolog()

           #init and push var
           self.c.LOAD_GLOBAL("PushVars")
           for e in self.locals[-1]:
              self.c.LOAD_CONST(e)
           self.c.BUILD_LIST(len(self.locals[-1]))
           self.c.CALL_FUNCTION(1,0)
           self.c.POP_TOP()
        
           #load arguments
           for e in self.locals[-1]:              
              self.c.LOAD_FAST(e)
              self.c.LOAD_FAST("#vars")
              self.c.LOAD_CONST(e)
              self.c.STORE_SUBSCR()


           self.c.LOAD_CONST(None) #Nil is default return value
           children[11]()
 
           #self.pprint("prepop: ")

           for r in self.returns:
              r()

           #restore var
           self.c.LOAD_GLOBAL("PopVars")
           for e in self.locals[-1]:
              self.c.LOAD_CONST(e)
           self.c.BUILD_LIST(len(self.locals[-1]))
           self.c.CALL_FUNCTION(1,0)
           self.c.POP_TOP()

           self.locals = self.locals[:-1]  
 
           #print "ssr: " + str(self.c.stack_size)

           self.c.RETURN_VALUE()

           f = new.function(self.c.code(),globals())
           skill.procedures[proc] = f
           skill.iprocs[proc] = f.__code__
           self.code_stack = self.code_stack[:-1]
           self.c = self.code_stack[-1]
           self.c.LOAD_CONST(True)
        return gen

    def visit_block(self,node,children):
        self.c.LOAD_CONST(None)
        self.prolog()
        if children[1]:
           children[1]()
        self.c.RETURN_VALUE()

    def visit_ws(self,node,visited_children):
        return None
     
    def generic_visit(self, node, visited_children):
        #try:
        #   print node.expr_name
        #except:
        #   pass
        if node and "".join(node.text.split()) == "":
           return None
        return visited_children or node

#iv = Visitor("")
#g =  grammar.parse(open("out.il","r").read())

c = """
procedure( fibonacci(n "d")
 d = n
 if(( n == 1 || n == 2) then
return(1)
else return(fibonacci(n-1) + fibonacci(n-2))
) ;this is a comment
)
"""

skill = new.module("skill")
skill.procedures = {}
skill.iprocs = {}
skill.variables = {}
skill.varstack = {}

#Code and evalstring() require different handling of parenthesis, fun
grammar = Grammar(grammar)

def update_grammar():
   grammar['func_name'].members = [Literal(x) for x in sorted(skill.procedures.keys(),key=lambda x: -len(x))]

def run(s,code=False):
   global iv
   breaks = []
   for m in re.finditer(r'\n', s):
         breaks.append(m.start())

   update_grammar()
   if code:
      g =  grammar.parse(s)#e)
      iv = Visitor(breaks,True)
   else:
      g =  grammar.parse(s)#e)
      iv = Visitor(breaks,False)

   #if not code:
   #   print g

   o = iv.visit(g)
   #Check if there are statements to perform
   r = new.function(iv.c.code(),globals())()
   print r
   return r

def load(f):
   return run(open(f,"r").read().split("#####")[0],True) 


def PushVars(l):
   for e in l:
     if e not in skill.varstack:
       skill.varstack[e] = []
     if e in skill.variables:
       skill.varstack[e].append(skill.variables[e])
     else:
       skill.varstack[e].append(None)
     skill.variables[e] = None

def PopVars(l):
   for e in l:
      skill.variables[e] = skill.varstack[e][-1]
      skill.varstack[e] = skill.varstack[e][:-1]

def unpickle_code(ms):
    co = marshal.loads(ms)
    assert isinstance(co, types.CodeType)
    return co

def pickle_code(co):
    assert isinstance(co, types.CodeType)
    ms = marshal.dumps(co)
    return unpickle_code, (ms,)

copyreg.pickle(types.CodeType, pickle_code, unpickle_code)

import runtime as runtime

cell_lib = {}
def layout(cell,extra_params=None):
   context.push()
   loadcell(cell)
   global pcell_updates
   for name,value in pcell_updates:
      context.bag[name]['value'] = value
      run(context.props['cbs'][name])
   pcell_updates = []

   #Must be called after pcell updates
   apply_params()

   if extra_params:
      assert(isinstance(extra_params,list))
      for t in extra_params:
         context.params[t[0]] = t[2]

   print "inst params: " + str(context.params)


   p = pickle.dumps(frozenset(context.params.items()))
   h = hashlib.md5(p).hexdigest()
   cell_name = current_cell['cell_name'] + "@" + h[:10]
   
   if cell_name in cell_lib:
     context.pop()
     return cell_lib[cell_name]
   runtime.push_cell(cell_name)
   print skill.procedures[current_cell['func']]({'parameters' : context.params, 'lib' : {'name' : skill.variables['cdfgData']['id']['lib']['name']} , 'cell' : {'name' : skill.variables['cdfgData']['id']['cell']['name']}} )
   context.pop()
   cell_lib[cell_name] = runtime.pop_cell()
   return cell_lib[cell_name]

def init(layermap):
   runtime.run(layermap,skill,run,layout)

def cload(code,version):
   compiled = code.split(".")[0] + ".ilc"
   h = hashlib.md5(open(code).read()).hexdigest()
   try:
      p = pickle.load( open( compiled, "rb" ) )
      assert(p['version'] == version)
      assert(p['code'] == code)
      assert(p['hash'] == h)
      #interp.skill.iprocs = p['functions']
      for k,v in p['functions'].iteritems():
          skill.procedures[k] = new.function(v,globals())
   except Exception as e:
      print "Compiling: " + code
      skill.iprocs = {} #clear already loaded functions
      load(code)
      p = { 'version' : version, 'code' : code, 'hash' : h, 'functions' : skill.iprocs}
      pickle.dump( p, open( compiled, "wb" ) )


def load_defaults(defaults):
   for e in defaults.split("("):
      e = e.split(")")[0].split()
      if len(e) < 3:
         continue
      v = None
      if e[1] == "string":
         context.params[e[0]] = str(e[2].split("\"")[1]) 
      elif e[1] == "boolean":
         context.params[e[0]] = e[2] == "t"
      elif e[1] == "float":
         context.params[e[0]] = float(e[2])
      elif e[1] == "int":
         context.params[e[0]] = int(e[2])

def load_props(props):
   runtime.load_props(props)

def apply_params():
   for k,v in context.bag.iteritems():
      if isinstance(v,dict):
         if 'value' in v:
            context.params[k] = v['value']

def cdfg_init(library,cell_name):
   skill.variables['cdfgData'] = context.bag
   skill.variables['cdfgData']['id'] = {'lib' : {'name' : library} , 'cell' : {'name' : cell_name}, 'libName' : library, 'cellName' : cell_name, 'name' : cell_name}
   skill.variables['cdfgData']['recall'] = {'value' : '0'}


def loadcell(cell):
   global current_cell
   #load defaults into interpreter
   current_cell = cell_defs[cell]
   context.params = tools.DerefDict()
   load_defaults(current_cell['defaults'])

   if "props" in current_cell:
      load_props(current_cell['props'])

   #This initializes the pcell callback stuff
   cdfg_init(current_cell['library'],current_cell['cell_name'])

cell_defs = {}
def load_cells(cells):
   for cell in cells:
      cell_defs[cell['cell_name']] = cell

pcell_updates = []
def pcell_apply(name,value):
   global pcell_updates
   pcell_updates.append((name,value))


