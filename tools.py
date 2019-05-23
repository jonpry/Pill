
class SkillTable(dict):
   def __init__(self,name="",default=None):
       self.name = name,
       self.default = default

   def __getitem__(self,key):
       if not key in self:
          return self.default
       return dict.__getitem__(self,key)

class Lazy(object):
    __ignore__ = "class mro new init setattr getattr getattribute ne cmp eq"

    def __init__(self, s,ev): 
         self.expr = s
         self.ev = ev
         self.obj = None
         
    def deref(self):
         if not self.obj:
            self.obj = self.ev(self.expr)

    def __ne__(self, b):
         if isinstance(b,Lazy):
            if self.expr == b.expr:
               return False
         if isinstance(b,basestring):
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
         if isinstance(b,basestring):
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
         if isinstance(b,basestring):
            if self.expr == b:
               return 0        
         self.deref()
         if isinstance(b,Lazy):
            b.deref()
            return self.obj.__cmp__(b.obj)
         return self.obj.__cmp__(b)

    # provide proxy access to regular attributes of wrapped object
    def __getattr__(self, name):
        print "lcall: " + name
        if not self.obj:
           self.obj = self.ev(self.expr)
        return getattr(self.obj, name)


    # create proxies for wrapped object's double-underscore attributes
    class __metaclass__(type):
        def __init__(cls, name, bases, dct):

            def make_proxy(name):
                def proxy(self, *args):
                    print "proxy: " + name
                    if not self.obj:
                       self.obj = self.ev(self.expr)
                    return getattr(self.obj, name)
                return proxy

            type.__init__(cls, name, bases, dct)
            ignore = set("__%s__" % n for n in cls.__ignore__.split())
            for name in dir(int) + dir(basestring) + dir(dict) + dir(list):
                if name.startswith("__"):
                    if name not in ignore and name not in dct:
                        #print name
                        setattr(cls, name, property(make_proxy(name)))

class DerefList(list):
   __ignore__ = "class mro new init setattr getattr getattribute"

   def __init__(self):
       pass

   def __getitem__(self,key):
       if isinstance(key,basestring):
           ret = []
           for e in self:
              ret.append(e[key])
           if len(ret)==1:
              return ret[0]
           return ret
       return list.__getitem__(self,key)

class DerefDict(dict):
   __ignore__ = "class mro new init setattr getattr getattribute"

   def __init__(self):
       pass

   def __getitem__(self,key):
       if dict.__contains__(self,key):
          return dict.__getitem__(self,key)

       print "************" + key
       ret = []
       for e in self:
          if key in e:
             ret.append(e[key])
 
       print "***********" + str(ret)
       if len(ret)==1:
          return ret[0]
       return ret


class SkillList(object):
    __ignore__ = "class mro new init setattr getattr getattribute"

    def __init__(self, l):
         self.obj = l
         self.singular = len(l) == 1
         
    # provide proxy access to regular attributes of wrapped object
    def __getattr__(self, name):
        print "lcall: " + name
        return getattr(self.obj, name)

    # create proxies for wrapped object's double-underscore attributes
    class __metaclass__(type):
        def __init__(cls, name, bases, dct):

            def make_proxy(name):
                def proxy(self, *args):
                    print "lproxy: " + name
                    if self.singular:
                        return getattr(self.obj[0], name)                        
                    return getattr(self.obj, name)
                return proxy

            type.__init__(cls, name, bases, dct)
            ignore = set("__%s__" % n for n in cls.__ignore__.split())
            for name in dir(int) + dir(float) + dir(basestring) + dir(dict) + dir(list):
                if name.startswith("__"):
                    if name not in ignore and name not in dct:
                        #print name
                        setattr(cls, name, property(make_proxy(name)))
 
