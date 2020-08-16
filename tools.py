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

class SkillTable(dict):
   def __init__(self,name="",default=None):
       self.name = name,
       self.default = default

   def __getitem__(self,key):
       if not key in self:
          return self.default
       return dict.__getitem__(self,key)

# create proxies for wrapped object's double-underscore attributes
class LazyMeta(type):
    def __init__(cls, name, bases, dct):
       def make_proxy(name):
            def proxy(self, *args):
                print("proxy: " + name)
                if not self.obj:
                   self.obj = self.ev(self.expr)
                return getattr(self.obj, name)
            return proxy

       type.__init__(cls, name, bases, dct)
       ignore = set("__%s__" % n for n in cls.__ignore__.split())
       for name in dir(int) + dir(str) + dir(dict) + dir(list):
           if name.startswith("__"):
               if name not in ignore and name not in dct:
                   #print(name)
                   setattr(cls, name, property(make_proxy(name)))


class Lazy(object,metaclass=LazyMeta):
    __ignore__ = "class mro new init setattr getattr getattribute ne cmp eq"

    def __init__(self, s,ev): 
         self.expr = s
         self.ev = ev
         self.obj = None
         
    def deref(self):
         if not self.obj:
            print("Beginning lazy eval")
            self.obj = self.ev(self.expr)
            print("End lazy eval")


    def __getitem__(self, key):
        self.deref()
        #print(self.obj)
        #assert(False)
        return self.obj[key]

    def __ne__(self, b):
         if isinstance(b,Lazy):
            if self.expr == b.expr:
               return False
         if isinstance(b,str):
            if self.expr == b:
               return False        
         if isinstance(b,Lazy):
            try:
               self.deref()
               b.deref()
               return self.obj != b
            except:
               return True
         self.deref()
         return self.obj != b

    def __eq__(self, b):
         if isinstance(b,Lazy):
            if self.expr == b.expr:
               return True
         if isinstance(b,str):
            if self.expr == b:
               return True         
         if isinstance(b,Lazy):
            try:
               self.deref()
               b.deref()
               return self.obj == b.obj
            except:
               return False
         self.deref()
         return self.obj == b

    def __cmp__(self, b):
         if isinstance(b,Lazy):
            if self.expr == b.expr:
               return 0
         if isinstance(b,str):
            if self.expr == b:
               return 0        
         self.deref()
         if isinstance(b,Lazy):
            b.deref()
            return self.obj.__cmp__(b.obj)
         return self.obj.__cmp__(b)

    # provide proxy access to regular attributes of wrapped object
    def __getattr__(self, name):
        print("lcall: " + name)
        if not self.obj:
           self.obj = self.ev(self.expr)
        return getattr(self.obj, name)

class SkillList(object):
    __ignore__ = "class mro new init setattr getattr getattribute"

    def __init__(self, l):
         self.obj = l
         self.singular = len(l) == 1
         
    # provide proxy access to regular attributes of wrapped object
    def __getattr__(self, name):
        print("lcall: " + name)
        return getattr(self.obj, name)

    # create proxies for wrapped object's double-underscore attributes
    class __metaclass__(type):
        def __init__(cls, name, bases, dct):

            def make_proxy(name):
                def proxy(self, *args):
                    print("lproxy: " + name)
                    if self.singular:
                        return getattr(self.obj[0], name)                        
                    return getattr(self.obj, name)
                return proxy

            type.__init__(cls, name, bases, dct)
            ignore = set("__%s__" % n for n in cls.__ignore__.split())
            for name in dir(int) + dir(float) + dir(str) + dir(dict) + dir(list):
                if name.startswith("__"):
                    if name not in ignore and name not in dct:
                        #print name
                        setattr(cls, name, property(make_proxy(name)))
 
