from array import array
from dis import *
from types import CodeType
from bytecode import Bytecode, Instr, Compare, SetLineno
import bytecode
import uuid
#from .symbol import Symbol
import sys

__all__ = [
    'Code', 'Const', 'Return', 'Global', 'Local', 'Call', 'const_value',
    'NotAConstant', 'Label', 'fold_args', 'nodetype', 'Node', 'Pass',
    'Compare', 'And', 'Or', 'Getattr', 'TryExcept', 'TryFinally', 'Suite',
    'LocalAssign', 'UnpackSequence', 'For', 'If', 'YieldStmt', 'Function',
    'ListComp', 'LCAppend',
]

opcode = {}
for op in range(256):
    name=opname[op]
    if name.startswith('<'): continue
    if name.endswith('+0'): opcode[name[:-2]]=op
    opcode[name]=op

print(opname)
print(opcode)

globals().update(opcode) # opcodes are now importable at will

# Flags from code.h
CO_OPTIMIZED              = 0x0001      # use LOAD/STORE_FAST instead of _NAME
CO_NEWLOCALS              = 0x0002      # only cleared for module/exec code
CO_VARARGS                = 0x0004
CO_VARKEYWORDS            = 0x0008
CO_NESTED                 = 0x0010      # ???
CO_GENERATOR              = 0x0020
CO_NOFREE                 = 0x0040      # set if no free or cell vars
CO_GENERATOR_ALLOWED      = 0x1000      # unused
CO_FUTURE_DIVISION        = 0x2000
CO_FUTURE_ABSOLUTE_IMPORT = 0x4000      # Python 2.5+ only
CO_FUTURE_WITH_STATEMENT  = 0x8000      # Python 2.5+ only

__all__.extend([k for k in globals().keys() if k.startswith('CO_')])

long = ord = int
unicode = basestring = str


fast_to_deref = {
    LOAD_FAST: LOAD_DEREF,
    STORE_FAST: STORE_DEREF,
}

deref_to_deref = dict([(k,k) for k in hasfree])

def with_name(f, name):
    try:
        f.__name__=name
        return f
    except (TypeError,AttributeError):
        return function(
            getattr(f,CODE), getattr(f,GLOBALS), name, getattr(f,DEFAULTS),
            getattr(f,CLOSURE)
        )


EXTRA_JUMPS = 'JUMP_IF_FALSE_OR_POP JUMP_IF_TRUE_OR_POP JUMP_IF_FALSE JUMP_IF_TRUE'.split()

class Label(bytecode.Label):
    """A forward-referenceable location in a ``Code`` object"""

    __slots__ = 'backpatches', 'resolution', 'id'

    def __init__(self):
        super(Label, self).__init__()
        self.backpatches = []
        self.resolution = None
        self.id = uuid.uuid4()

    def SETUP_EXCEPT(self, code):
        code.SETUP_EXCEPT(); self.backpatches.append(code.blocks[-1][-1])

    def SETUP_FINALLY(self, code):
        code.SETUP_FINALLY(); self.backpatches.append(code.blocks[-1][-1])

    def SETUP_LOOP(self, code):
        code.SETUP_LOOP(); self.backpatches.append(code.blocks[-1][-1])

    def POP_BLOCK(self, code):
        self.backpatches[0] = code.POP_BLOCK()

    for name in [opname[op] for op in hasjrel+hasjabs]+EXTRA_JUMPS:
        if name not in locals():
            def do_jump(self, code, name=name):
                method = getattr(code, name)
                if self.resolution is None:
                    return self.backpatches.append(method())
                else:
                    return method(self.resolution)
            locals()[name] = with_name(do_jump, name)
    del do_jump

    def __call__(self, code):
        if self.resolution is not None:
            raise AssertionError("Label previously defined")
        self.resolution = resolution = len(code.co_code)
        for p in self.backpatches:
            if p: p()

labelMap = {}

class Code(object):
    co_argcount = 0
    co_stacksize = 0
    co_flags = CO_OPTIMIZED | CO_NEWLOCALS      # typical usage
    co_filename = '<generated code>'
    co_name = '<lambda>'
    co_firstlineno = 0
    co_freevars = ()
    co_cellvars = ()
    _last_lineofs = 0
    _last_line = 0
    _ss = 0
    _tmp_level = 0

    def __init__(self):
        self.co_code = Bytecode()
        self.co_consts = [None]
        self.co_names = []
        self.co_varnames = []
        self.co_lnotab = array('B')
        self.blocks = []
        self.stack_history = []

    def emit_arg(self, op, arg):
        self.co_code.append(Instr(op,arg))

    def locals_written(self):
        vn = self.co_varnames
        hl = dict.fromkeys([STORE_FAST, DELETE_FAST])
        return dict.fromkeys([vn[arg] for ofs, op, arg in self if op in hl])

    def set_lineno(self, lno):
        if(lno > 0):
           self.co_code.append(SetLineno(lno))

        if not self.co_firstlineno:
            self.co_firstlineno = self._last_line = lno
            return

        append = self.co_lnotab.append
        incr_line = lno - self._last_line
        incr_addr = len(self.co_code) - self._last_lineofs
        if not incr_line:
            return

        if incr_addr<=0 or incr_line<=0:
             return

        while incr_addr>255:
            append(255)
            append(0)
            incr_addr -= 255

        while incr_line>255:
            append(incr_addr)
            append(255)
            incr_line -= 255
            incr_addr = 0

        if incr_addr or incr_line:
            append(incr_addr)
            append(incr_line)

        self._last_line = lno
        self._last_lineofs = len(self.co_code)

    def YIELD_VALUE(self):
        self.stackchange(stack_effects[YIELD_VALUE])
        self.co_flags |= CO_GENERATOR
        return self.emit(YIELD_VALUE)


    def LOAD_CONST(self, const):
        self.stackchange((0,1))
        pos = 0
        hashable = True
        try:
            hash(const)
        except TypeError:
            hashable = False
        while 1:
            try:
                arg = self.co_consts.index(const, pos)
                it = self.co_consts[arg]
            except ValueError:
                arg = len(self.co_consts)
                self.co_consts.append(const)
                break
            else:
                if type(it) is type(const) and (hashable or it is const):
                    break
            pos = arg+1
            continue
        return self.emit_arg('LOAD_CONST', const)

    def CALL_FUNCTION(self, argc=0, foo=0, op='CALL_FUNCTION', extra=0):
        self.stackchange((1+argc+extra,1))
        self.emit_arg(op,argc);

    def CALL_FUNCTION_VAR(self, argc=0, kwargc=0):
        assert(False)
        self.CALL_FUNCTION(argc,kwargc,CALL_FUNCTION_VAR, 1)    # 1 for *args

    def CALL_FUNCTION_KW(self, argc=0, kwargc=0):
        self.stackchange((2+argc+kwargc,1))
        self.emit_arg('CALL_FUNCTION_KW', argc+kwargc)

    def CALL_FUNCTION_VAR_KW(self, argc=0, kwargc=0):
        assert(False)
        self.CALL_FUNCTION(argc,kwargc,CALL_FUNCTION_VAR_KW, 2) # 2 *args,**kw


    def CALL_METHOD(self, argc=0, foo=0):
        self.stackchange((2+argc,1))
        self.emit_arg('CALL_METHOD',argc);

    def BUILD_TUPLE(self, count):
        self.stackchange((count,1))
        self.emit_arg('BUILD_TUPLE',count)

    def BUILD_LIST(self, count):
        self.stackchange((count,1))
        self.emit_arg('BUILD_LIST',count)

    def BUILD_MAP(self, count):
        self.stackchange((count*2,1))
        self.emit_arg('BUILD_MAP',count)

    def UNPACK_SEQUENCE(self, count):
        self.stackchange((1,count))
        self.emit_arg('UNPACK_SEQUENCE',count)

    def RETURN_VALUE(self):
        self.stackchange((1,0))
        self.co_code.append(Instr('RETURN_VALUE'))
        self.stack_unknown()

    def BUILD_SLICE(self, count):
        assert count in (2,3), "Invalid number of arguments for BUILD_SLICE"
        self.stackchange((count,1))
        self.emit_arg(BUILD_SLICE,count)

    def DUP_TOPX(self, count):
        self.stackchange((count,count*2))
        self.emit_arg(DUP_TOPX,count)

    def RAISE_VARARGS(self, argc):
        assert 0<=argc<=3, "Invalid number of arguments for RAISE_VARARGS"
        self.stackchange((argc,0))
        self.emit_arg(RAISE_VARARGS,argc)

    def MAKE_FUNCTION(self, ndefaults):
        self.stackchange((1+ndefaults,1))
        self.emit_arg(MAKE_FUNCTION, ndefaults)

    def MAKE_CLOSURE(self, ndefaults, freevars):
        if sys.version>='2.5':
            freevars = 1
        self.stackchange((1+freevars+ndefaults,1))
        self.emit_arg(MAKE_CLOSURE, ndefaults)

    def here(self):
        return len(self.co_code)

    def curPos(self):
        label = Label()
        self.co_code.append(label)
        labelMap[label.id] = len(self.co_code)
        return label

    if 'UNARY_CONVERT' not in opcode:
        def UNARY_CONVERT(self):
            self(Const(repr))
            self.ROT_TWO()
            self.CALL_FUNCTION(1, 0)

    if 'BINARY_DIVIDE' not in opcode:
        def BINARY_DIVIDE(self):
            self.BINARY_TRUE_DIVIDE()

    if 'DUP_TOPX' not in opcode:
        def DUP_TOPX(self, count):
            self.stackchange((count,count*2))
            if count==2:
                self.emit(DUP_TOP_TWO)
            else:
                raise RuntimeError("Python 3 only supports DUP_TOP_TWO")

    if 'SLICE_0' not in opcode:
        def SLICE_0(self):
            self(None, None, Code.SLICE_3)
        def SLICE_1(self):
            self(None, Code.SLICE_3)
        def SLICE_2(self):
            self(None, Code.ROT_TWO, Code.SLICE_3)
        def SLICE_3(self):
            self.BUILD_SLICE(2)
            self.BINARY_SUBSCR()           
            

    def set_stack_size(self, size):
        if size<0:
            raise AssertionError("Stack underflow")
        if size>self.co_stacksize:
            self.co_stacksize = size
        bytes = len(self.co_code) - len(self.stack_history) + 1
        if bytes>0:
            self.stack_history.extend([self._ss]*bytes)
        self._ss = size


    def get_stack_size(self):
        return self._ss

    stack_size = property(get_stack_size, set_stack_size)

    def stackchange(self, inout):
        (inputs,outputs) = inout
        if self._ss is None:
            raise AssertionError("Unknown stack size at this location")
        self.stack_size -= inputs   # check underflow
        self.stack_size += outputs  # update maximum height


    def stack_unknown(self):
        self._ss = None

    def branch_stack(self, location, expected):
        location = labelMap[location.id]
        if location >= len(self.stack_history):
            if location > len(self.co_code):
                raise AssertionError("Forward-looking stack prediction!",
                    location, len(self.co_code)
                )
            actual = self.stack_size
            if actual is None:
                self.stack_size = actual = expected
                self.stack_history[location] = actual
        else:
            actual = self.stack_history[location]
            if actual is None:
                self.stack_history[location] = actual = expected

        if actual != expected:
            raise AssertionError(
                "Stack level mismatch: actual=%s expected=%s"
                % (actual, expected)
            )





    def jump(self, op, arg=None):
        def backpatch(offset):
            assert(op!=120)
            #self.patch_arg(posn, 0x1FFFF, target,op)
            self.branch_stack(offset, old_level)

        if op==FOR_ITER:
            old_level = self.stack_size = self.stack_size - 1
            self.stack_size += 2
        else:
            old_level = self.stack_size
        self.stack_size -= (op in (JUMP_IF_TRUE_OR_POP, JUMP_IF_FALSE_OR_POP))
        posn = self.here()
        if arg is not None:
            #print("jt: " + hex(jump_target(arg)))
            self.emit_arg(opname[op], arg)
            self.branch_stack(arg, old_level)
            lbl = None
        else:
            label = Label()
            self.emit_arg(opname[op], label)
            def lbl(code=None,label=label):
                self.co_code.append(label)
                labelMap[label.id] = len(self.co_code)
                backpatch(label)
        if op in (JUMP_FORWARD, JUMP_ABSOLUTE, CONTINUE_LOOP):
            self.stack_unknown()
        return lbl

    def COMPARE_OP(self, op):
        self.stackchange((2,1))
        self.emit_arg('COMPARE_OP', compares[op])

    def setup_block(self, op):
        jmp = self.jump(op)
        self.blocks.append((op,self.stack_size,jmp))
        return jmp

    def SETUP_EXCEPT(self):
        ss = self.stack_size
        self.stack_size = ss+3  # simulate the level at "except:" time
        self.setup_block(SETUP_EXCEPT)
        self.stack_size = ss    # restore the current level

    def SETUP_FINALLY(self):
        ss = self.stack_size
        self.stack_size = ss+3  # allow for exceptions
        self.stack_size = ss+1  # simulate the level after the None is pushed
        self.setup_block(SETUP_FINALLY)
        self.stack_size = ss    # restore original level

    def SETUP_LOOP(self):
        self.setup_block(SETUP_LOOP)

    def POP_BLOCK(self):
        if not self.blocks:
            raise AssertionError("Not currently in a block")

        why, level, fwd = self.blocks.pop()
        self.emit(POP_BLOCK)

        if why!=SETUP_LOOP:
            if why==SETUP_FINALLY:
                self.LOAD_CONST(None)
                fwd()
            else:
                self.stack_size = level-3   # stack level resets here
                else_ = self.JUMP_FORWARD()
                fwd()
                return else_
        else:
            return fwd


    if 'JUMP_IF_TRUE_OR_POP' not in opcode:
        def JUMP_IF_TRUE_OR_POP(self, address=None):
            lbl = self.JUMP_IF_TRUE(address)
            self.POP_TOP()
            return lbl
        globals()['JUMP_IF_TRUE_OR_POP'] = -1

    if 'JUMP_IF_FALSE_OR_POP' not in opcode:
        def JUMP_IF_FALSE_OR_POP(self, address=None):
            lbl = self.JUMP_IF_FALSE(address)
            self.POP_TOP()
            return lbl
        globals()['JUMP_IF_FALSE_OR_POP'] = -1

    if 'JUMP_IF_TRUE' not in opcode:
        def JUMP_IF_TRUE(self, address=None):
            self.DUP_TOP()
            return self.POP_JUMP_IF_TRUE(address)
    else:
        globals()['POP_JUMP_IF_TRUE'] = -1

    if 'JUMP_IF_FALSE' not in opcode:
        def JUMP_IF_FALSE(self, address=None):
            self.DUP_TOP()
            return self.POP_JUMP_IF_FALSE(address)
    else:
        globals()['POP_JUMP_IF_FALSE'] = -1

    if 'LIST_APPEND' in opcode and LIST_APPEND>=HAVE_ARGUMENT:
        def LIST_APPEND(self, depth):
            self.stackchange((depth+1, depth))
            self.emit_arg(LIST_APPEND, depth)









    def assert_loop(self):
        for why,level,fwd in self.blocks:
            if why==SETUP_LOOP:
                return
        raise AssertionError("Not inside a loop")

    def BREAK_LOOP(self):
        self.assert_loop(); self.emit(BREAK_LOOP)
        self.stack_unknown()

    def CONTINUE_LOOP(self, label):
        self.assert_loop()
        if self.blocks[-1][0]==SETUP_LOOP:
            op = JUMP_ABSOLUTE  # more efficient if not in a nested block
        else:
            op = CONTINUE_LOOP
        return self.jump(op, label)

    def __call__(self, *args):
        last = None
        for ob in args:
            if hasattr(ob, '__call__'):
                last = ob(self)
            else:
                try:
                    f = generate_types[type(ob)]
                except KeyError:
                    raise TypeError("Can't generate", ob)
                else:
                    last = f(self, ob)
        return last

    def return_(self, ob=None):
        return self(ob, Code.RETURN_VALUE)

    @classmethod
    def from_function(cls, function, copy_lineno=False):
        code = cls.from_code(getattr(function, CODE), copy_lineno)
        return code


    @classmethod
    def from_code(cls, code, copy_lineno=False):
        import inspect
        self = cls.from_spec(code.co_name, *inspect.getargs(code))
        if copy_lineno:
            self.set_lineno(code.co_firstlineno)
            self.co_filename = code.co_filename
        self.co_freevars = code.co_freevars     # XXX untested!
        return self

    @classmethod
    def from_spec(cls, name='<lambda>', args=(), var=None, kw=None):
        self = cls()
        self.co_name = name
        self.co_argcount = len(args)
        self.co_varnames.extend(args)
        if var:
            self.co_varnames.append(var)
            self.co_flags |= CO_VARARGS
        if kw:
            self.co_varnames.append(kw)
            self.co_flags |= CO_VARKEYWORDS

        def tuple_arg(args):
            self.UNPACK_SEQUENCE(len(args))
            for arg in args:
                if not isinstance(arg, basestring):
                    tuple_arg(arg)
                else:
                    self.STORE_FAST(arg)

        for narg, arg in enumerate(args):
            if not isinstance(arg, basestring):
                dummy_name = '.'+str(narg)
                self.co_varnames[narg] = dummy_name
                self.LOAD_FAST(dummy_name)
                tuple_arg(arg)

        return self


    def patch_arg(self, offset, oldarg, newarg, op):
        assert(op!=120)	
        code = self.co_code
        if (newarg>0xFFFF) and (oldarg<=0xFFFF):
            raise AssertionError("Can't change argument size", oldarg, newarg)
        code[offset+1] = newarg & 255
        code[offset+2] = (newarg>>8) & 255
        if newarg>0xFFFF or oldarg>0xFFFF or op == 120:
            code[offset+1] = (newarg>>16) & 255
            code[offset+2] = (newarg>>24) & 255
            code[offset+4] = (newarg>>0) & 255
            code[offset+5] = (newarg>>8) & 255

    def nested(self, name='<lambda>', args=(), var=None, kw=None, cls=None):
        if cls is None:
            cls = self.__class__
        code = cls.from_spec(name, args, var, kw)
        code.co_filename=self.co_filename
        return code

    def __iter__(self):
        i = 0
        extended_arg = 0
        code = self.co_code
        n = len(code)
        while i < n:
            op = code[i]
            if op >= HAVE_ARGUMENT:
                oparg = code[i+1] + code[i+2]*256 + extended_arg
                extended_arg = 0
                if op == EXTENDED_ARG:
                    extended_arg = oparg*long(65536)
                    i+=3
                    continue
                yield i, op, oparg
                i += 3
            else:
                yield i, op, None
                i += 1




    def makefree(self, names):
        nowfree = dict.fromkeys(self.co_freevars)
        newfree = [n for n in names if n not in nowfree]
        if newfree:
            self.co_freevars += tuple(newfree)
            self._locals_to_cells()

    def makecells(self, names):
        nowcells = dict.fromkeys(self.co_cellvars+self.co_freevars)
        newcells = [n for n in names if n not in nowcells]
        if newcells:
            if not (self.co_flags & CO_OPTIMIZED):
                raise AssertionError("Can't use cellvars in unoptimized scope")
            cc = len(self.co_cellvars)
            nc = len(newcells)
            self.co_cellvars += tuple(newcells)
            if self.co_freevars:
                self._patch(
                    deref_to_deref,
                    dict([(n+cc,n+cc+nc)for n in range(len(self.co_freevars))])
                )
            self._locals_to_cells()

    def _locals_to_cells(self):
        freemap = dict(
            [(n,p) for p,n in enumerate(self.co_cellvars+self.co_freevars)]
        )
        argmap = dict(
            [(p,freemap[n]) for p,n in enumerate(self.co_varnames)
                if n in freemap]
        )
        if argmap:
            for ofs, op, arg in self:
                if op==DELETE_FAST and arg in argmap:
                    raise AssertionError(
                        "Can't delete local %r used in nested scope"
                        % self.co_varnames[arg]
                    )
            self._patch(fast_to_deref, argmap)


    def _patch(self, opmap, argmap={}):
        code = self.co_code
        for ofs, op, arg in self:
            if op in opmap:
                print(op)
                if arg in argmap:
                    self.patch_arg(ofs, arg, argmap[arg],op)
                elif arg is not None:
                    continue
                code[ofs] = opmap[op]

    def code(self, parent=None):
        if self.blocks:
            raise AssertionError("%d unclosed block(s)" % len(self.blocks))

        flags = self.co_flags & ~CO_NOFREE
        if parent is not None:
            locals_written = self.locals_written()
            self.makefree([
                n for n in self.co_varnames[
                    self.co_argcount
                    + ((self.co_flags & CO_VARARGS)==CO_VARARGS)
                    + ((self.co_flags & CO_VARKEYWORDS)==CO_VARKEYWORDS)
                    :
                ] if n not in locals_written
            ])

        if not self.co_freevars and not self.co_cellvars:
            flags |= CO_NOFREE
        elif parent is not None and self.co_freevars:
            parent.makecells(self.co_freevars)

        self.co_code.argcount = self.co_argcount;
        self.co_code.argnames = self.co_varnames[:self.co_argcount];
        self.co_code.name = self.co_name;
        self.co_code.filename = self.co_filename;
        for e in self.co_code:
          print(e)
        return self.co_code.to_code();


for op in hasfree:
    if not hasattr(Code, opname[op]):
        def do_free(self, varname, op=op):
            self.stackchange(stack_effects[op])
            try:
                arg = list(self.co_cellvars+self.co_freevars).index(varname)
            except ValueError:
                raise NameError("Undefined free or cell var", varname)
            self.emit_arg(op, arg)
        setattr(Code, opname[op], with_name(do_free, opname[op]))

compares = { '==' : Compare.EQ, '!=' : Compare.NE, '>' : Compare.GT, '>=' : Compare.GE,
             '<' : Compare.LT, '<=' : Compare.LE, "in" : Compare.IN, "is" : Compare.IS}

for op in hasname:
    if not hasattr(Code, opname[op]):
        def do_name(self, name, op=op):
            self.stackchange(stack_effects[op])

            self.emit_arg(opname[op], name)
            if op in (LOAD_NAME, STORE_NAME, DELETE_NAME):
                # Can't use optimized local vars, so reset flags
                self.co_flags &= ~CO_OPTIMIZED
        setattr(Code, opname[op], with_name(do_name, opname[op]))


for op in haslocal:
    if not hasattr(Code, opname[op]):
        def do_local(self, varname, op=op):
            if not self.co_flags & CO_OPTIMIZED:
                raise AssertionError(
                    "co_flags must include CO_OPTIMIZED to use fast locals"
                )
            self.stackchange(stack_effects[op])
            self.emit_arg(opname[op], varname)
        setattr(Code, opname[op], with_name(do_local, opname[op]))

for op in hasjrel+hasjabs:
    if not hasattr(Code, opname[op]):
        def do_jump(self, address=None, op=op):
            self.stackchange(stack_effects[op])
            return self.jump(op, address)
        setattr(Code, opname[op], with_name(do_jump, opname[op]))


def gen_map(code, ob):
    code.BUILD_MAP(0)
    for k,v in ob.items():
        code.DUP_TOP()
        code(k, v)
        code.ROT_THREE()
        code.STORE_SUBSCR()

def gen_tuple(code, ob):
    code(*ob)
    return code.BUILD_TUPLE(len(ob))

def gen_list(code, ob):
    code(*ob)
    return code.BUILD_LIST(len(ob))

def gen_const(code, ob):
    print(code)
    assert(False)

generate_types = {
    int:        gen_const,
    long:       gen_const,
    bool:       gen_const,
    CodeType:   gen_const,
    str:        gen_const,
    unicode:    gen_const,
    complex:    gen_const,
    float:      gen_const,
    type(None): gen_const,
    tuple:      gen_tuple,
    list:       gen_list,
    dict:       gen_map,
}



class NotAConstant(Exception):
    """The supplied value is not a constant expression tree"""


def const_value(value):
    """Return the constant value -- if any -- of an expression tree

    Raises NotAConstant if the value or any child of the value are
    not constants.
    """
    t = type(value)
    if t is Const:
        value = value.value
    elif t is tuple:
        t = tuple(map(const_value,value))
        if t==value:
            return value
        return t
    elif generate_types.get(t) != Code.LOAD_CONST:
        raise NotAConstant(value)
    return value


def fold_args(f, *args):
    """Return a folded ``Const`` or an argument tuple"""

    try:
        for arg in args:
            if arg is not Pass and arg is not None:
                const_value(arg)
    except NotAConstant:
        return args
    else:
        c = Code()
        f(*args+(c,))
        c.RETURN_VALUE()
        return Const(eval(c.code()))




def iter_code(codestring):
    """Iterate over a code string, yielding (start,op,arg,jump,end) tuples

    `start` is the position of the operation start, `end` is the position of
    the next operation start.  `jump` is a jump target or ``None`` if `op`
    isn't a jump.  `op` is the opcode, and `arg` the argument, with 32-bit
    ``EXTENDED_ARG`` instructions pre-processed.
    """
    start = ptr = 0
    size = len(codestring)
    extend = 0
    while ptr < size:
        op = ord(codestring[ptr])
        ptr += 1
        if op>=HAVE_ARGUMENT:
            arg = ord(codestring[ptr]) + ord(codestring[ptr+1])*256 + extend
            extended_arg = 0
            ptr += 2
            if op == EXTENDED_ARG:
                extend = arg*long(65536)
                continue
            if op in hasjrel or op in hasjabs:
                jump = arg+ptr*(op in hasjrel)
            else:
                jump = None
        else:
            arg = label = jump = None
        yield start, op, arg, jump, ptr
        start = ptr

argtype = {}
for name, group in dict(
    co_consts = hasconst,
    co_names = hasname,
    co_varnames = haslocal,
    free = hasfree,
    cmp_ops = hascompare,
).items():
    for op in group:
        argtype[op] = name

def dump(code):
    """Disassemble code in a symbolic manner, i.e., without offsets"""
    code = getattr(code, FUNC, code)
    code = getattr(code, CODE, code)
    co_names = code.co_names
    co_consts = [repr(x) for x in code.co_consts]
    co_varnames = code.co_argnames
    cmp_ops = cmp_op
    free = code.co_cellvars + code.co_freevars
    labels = {}
    instructions = list(iter_code(code.co_code))
    lbl = [jump for start, op, arg, jump, end in instructions if jump is not None]
    lbl.sort()
    for jump in lbl:
        labels.setdefault(jump, "L%d:" % (len(labels)+1))

    i = 0
    while i<len(instructions):
        start, op, arg, jump, end = instructions[i]
        ln = '        '+labels.get(start, '').ljust(7)
        if op==DUP_TOP and instructions[i+1][1] in (POP_JUMP_IF_FALSE, POP_JUMP_IF_TRUE):
            s, op, arg, jump, end = instructions[i+1]
            ln+=' '+['JUMP_IF_FALSE', 'JUMP_IF_TRUE'][op==POP_JUMP_IF_TRUE].ljust(15)
            i+=1
        elif op in (JUMP_IF_TRUE_OR_POP, JUMP_IF_FALSE_OR_POP):
            ln += ' ' + opname[op][:-7].ljust(15)
        else:
            ln += ' ' + opname[op].ljust(15)
        if jump is not None:
            ln += ' ' + labels[jump][:-1].rjust(10)
        elif arg is not None:
            ln += ' ' + repr(arg).rjust(10)
            if op in argtype:
                ln += ' (%s)' % (locals()[argtype[op]][arg])
        print(ln)
        if op in (JUMP_IF_TRUE_OR_POP, JUMP_IF_FALSE_OR_POP):
            print('        '+''.ljust(7) + ' POP_TOP')
        i+=1



class _se:
    """Quick way of defining static stack effects of opcodes"""
    POP_TOP   = END_FINALLY = POP_JUMP_IF_FALSE = POP_JUMP_IF_TRUE = 1,0
    ROT_TWO   = 2,2
    ROT_THREE = 3,3
    ROT_FOUR  = 4,4
    DUP_TOP   = 1,2
    UNARY_POSITIVE = UNARY_NEGATIVE = UNARY_NOT = UNARY_CONVERT = \
        UNARY_INVERT = GET_ITER = LOAD_ATTR = IMPORT_FROM = 1,1

    BINARY_POWER = BINARY_MULTIPLY = BINARY_DIVIDE = BINARY_FLOOR_DIVIDE = \
        BINARY_TRUE_DIVIDE = BINARY_MODULO = BINARY_ADD = BINARY_SUBTRACT = \
        BINARY_SUBSCR = BINARY_LSHIFT = BINARY_RSHIFT = BINARY_AND = \
        BINARY_XOR = BINARY_OR = COMPARE_OP = 2,1

    INPLACE_POWER = INPLACE_MULTIPLY = INPLACE_DIVIDE = \
        INPLACE_FLOOR_DIVIDE = INPLACE_TRUE_DIVIDE = INPLACE_MODULO = \
        INPLACE_ADD = INPLACE_SUBTRACT = INPLACE_LSHIFT = INPLACE_RSHIFT = \
        INPLACE_AND = INPLACE_XOR = INPLACE_OR = 2,1

    SLICE_0, SLICE_1, SLICE_2, SLICE_3 = \
        (1,1),(2,1),(2,1),(3,1)
    STORE_SLICE_0, STORE_SLICE_1, STORE_SLICE_2, STORE_SLICE_3 = \
        (2,0),(3,0),(3,0),(4,0)
    DELETE_SLICE_0, DELETE_SLICE_1, DELETE_SLICE_2, DELETE_SLICE_3 = \
        (1,0),(2,0),(2,0),(3,0)
    
    STORE_SUBSCR = POP_EXCEPT = EXEC_STMT = 3,0
    DELETE_SUBSCR = STORE_ATTR = 2,0
    DELETE_ATTR = STORE_DEREF = 1,0
    PRINT_EXPR = PRINT_ITEM = PRINT_NEWLINE_TO = IMPORT_STAR = 1,0
    RETURN_VALUE = YIELD_VALUE = STORE_NAME = STORE_GLOBAL = STORE_FAST = 1,0
    PRINT_ITEM_TO = LIST_APPEND = 2,0

    LOAD_LOCALS = LOAD_CONST = LOAD_NAME = LOAD_GLOBAL = LOAD_FAST = \
        LOAD_CLOSURE = LOAD_DEREF = IMPORT_NAME = BUILD_MAP = 0,1

    BUILD_CLASS = 3,1
    JUMP_IF_TRUE = JUMP_IF_FALSE = \
        JUMP_IF_TRUE_OR_POP = JUMP_IF_FALSE_OR_POP = 1,1

if sys.version>="2.5":
    _se.YIELD_VALUE = 1, 1

stack_effects = [(0,0)]*256

for name in opcode:
    op = opcode[name]
    name = name.replace('+','_')

    if hasattr(_se,name):
        # update stack effects table from the _se class
        stack_effects[op] = getattr(_se,name)

    if not hasattr(Code,name):
        # Create default method for Code class
        if op>=HAVE_ARGUMENT:
            def do_op(self,arg,op=op,se=stack_effects[op]):
                self.stackchange(se); self.emit_arg(op,arg)
        else:
            def do_op(self,op=op,se=stack_effects[op],name=name):
                self.stackchange(se); self.co_code.append(Instr(name))

        setattr(Code, name, with_name(do_op, name))


















