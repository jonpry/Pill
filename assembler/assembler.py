from array import array
from dis import *
from types import CodeType
from peak.util.symbols import Symbol
from peak.util.decorators import decorate_assignment, decorate
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



to_code = lambda x: x.tostring()

try:
    from new import code as NEW_CODE, function
except ImportError:
    from types import FunctionType as function
    NEW_CODE = lambda ac, *args: CodeType(ac, 0, *args)
    long = ord = int
    unicode = basestring = str
    def to_code(x):
        global to_code
        if not hasattr(x, 'tobytes'):
            to_code = lambda x: x.tostring()
        else:
            to_code = lambda x: x.tostring()
        return to_code(x)

    CODE, GLOBALS, DEFAULTS, CLOSURE, FUNC  = (
        '__code__', '__globals__', '__defaults__', '__closure__', '__func__'
    )
else:
    CODE, GLOBALS, DEFAULTS, CLOSURE, FUNC  = (
        'func_code', 'func_globals', 'func_defaults', 'func_closure', 'im_func'
    )
    ord = ord
















class Const(object):
    """Wrapper to ensure constants are hashable even if mutable"""

    __slots__ = 'value', 'hash', 'hashable'
    def __init__(self, value):
        self.value = value
        try:
            self.hash = hash(value)
        except TypeError:
            self.hash = hash(id(value))
            self.hashable = False
        else:
            self.hashable = True

    def __repr__(self):
        return "Const(%s)" % repr(self.value)

    def __hash__(self):
        return self.hash

    def __eq__(self, other):
        if type(other) is not Const:
            return False
        if self.hashable:
            return self.value == other.value
        else:
            return self.value is other.value

    def __ne__(self, other):
        return not self==other

    def __call__(self, code):
        code.LOAD_CONST(self.value)








class Node(tuple):
    """Base class for AST nodes"""
    __slots__ = []
    __hash__ = tuple.__hash__

def nodetype(*mixins, **kw):

    def callback(frame, name, func, old_locals):
        def __new__(cls, *args, **kw):
            result = func(*args, **kw)
            if type(result) is tuple:
                return tuple.__new__(cls, (cls,)+result)
            else:
                return result

        def __repr__(self):
            r = self.__class__.__name__ + tuple.__repr__(self[1:])
            if len(self)==2: return r[:-2]+')'  # nix trailing ','
            return r

        def __call__(self, code):
            return func(*(self[1:]+(code,)))

        import inspect
        args = inspect.getargspec(func)[0]

        d = dict(
            __new__ = __new__, __repr__ = __repr__, __doc__=func.__doc__,
            __module__ = func.__module__, __args__ = args, __slots__ = [],
            __call__ = __call__
        )
        for p,a in enumerate(args[:-1]):    # skip 'code' argument
            if isinstance(a,str):
                d[a] = property(lambda self, p=p+1: self[p])

        d.update(kw)
        return type(name, mixins+(Node,), d)

    return decorate_assignment(callback)


nodetype()
def Global(name, code=None):
    if code is None:
        return name,
    code.LOAD_GLOBAL(name)

nodetype()
def Local(name, code=None):
    if code is None:
        return name,
    if name in code.co_cellvars or name in code.co_freevars:
        return code.LOAD_DEREF(name)
    elif code.co_flags & CO_OPTIMIZED:
        return code.LOAD_FAST(name)
    else:
        return code.LOAD_NAME(name)

nodetype()
def Return(value=None, code=None):
    if code is None:
        return value,
    return code(value, Code.RETURN_VALUE)

class _Pass(Symbol):
    def __call__(self, code=None):
        pass
    def __nonzero__(self):
        return False
Pass = _Pass('Pass', __name__)

nodetype()
def Getattr(ob, name, code=None):
    try:
        name = const_value(name)
    except NotAConstant:
        return Call(Const(getattr), [ob, name])
    if code is None:
        return fold_args(Getattr, ob, name)
    code(ob)
    code.LOAD_ATTR(name)

nodetype()
def Call(func, args=(),kwargs=(), star=None,dstar=None, fold=True, code=None):
    if code is None:
        data = (
            func, tuple(args), tuple(kwargs), star or (), dstar or (), fold
        )
        if fold and (args or kwargs or star or dstar):
            return fold_args(Call, *data)
        else:
            return data

    code(func, *args)
    for k,v in kwargs:
        code(k,v)

    argc = len(args)
    kwargc = len(kwargs)

    if star:
        if dstar:
            code(star, dstar)
            return code.CALL_FUNCTION_VAR_KW(argc, kwargc)
        else:
            code(star)
            return code.CALL_FUNCTION_VAR(argc, kwargc)
    else:
        if dstar:
            code(dstar)
            return code.CALL_FUNCTION_KW(argc, kwargc)
        else:
            return code.CALL_FUNCTION(argc, kwargc)










nodetype()
def TryExcept(body, handlers, else_=Pass, code=None):
    if code is None:
        return body, tuple(handlers), else_
    okay = Label()
    done = Label()
    code(okay.SETUP_EXCEPT, body, okay.POP_BLOCK)
    if 'POP_EXCEPT' in opcode:
        code.stack_size += 3
    for typ, handler in handlers:
        next_test = Label()
        Compare(Code.DUP_TOP, [('exception match', typ)], code)
        code(
            next_test.JUMP_IF_FALSE_OR_POP,             # remove condition
            Code.POP_TOP, Code.POP_TOP, Code.POP_TOP,   # remove exc info
        )
        if 'POP_EXCEPT' in opcode:
            code(Code.POP_EXCEPT)
        code(handler)
        if code.stack_size is not None:
            code(done.JUMP_FORWARD)
        code(next_test, Code.POP_TOP)            # remove condition
    code(Code.END_FINALLY)
    code.stack_unknown()    # force stack level to come from end of body
    code(okay, else_, done)

nodetype()
def Suite(body, code=None):
    if code is None:
        if body: return tuple(body),
        return Pass
    code(*body)

nodetype()
def TryFinally(body, handler, code=None):
    if code is None:
        return body, handler
    code(
        Code.SETUP_FINALLY, body, Code.POP_BLOCK, handler, Code.END_FINALLY
    )

nodetype()
def LocalAssign(name, code=None):
    if code is None:
        return name,
    if name in code.co_cellvars or name in code.co_freevars:
        return code.STORE_DEREF(name)
    elif code.co_flags & CO_OPTIMIZED:
        return code.STORE_FAST(name)
    else:
        return code.STORE_NAME(name)


nodetype()
def UnpackSequence(nodes, code=None):
    if code is None:
        return tuple(nodes),
    code.UNPACK_SEQUENCE(len(nodes))
    return code(*nodes)


nodetype()
def For(iterable, assign, body=Pass, code=None):
    if code is None:
        return iterable, assign, body
    L1, L2 = Label(), Label()
    return code(
        iterable, Code.GET_ITER, L1, L2.FOR_ITER, assign, body,
        L1.JUMP_ABSOLUTE, L2
    )


nodetype()
def YieldStmt(value=None, code=None):
    if code is None:
        return value,
    r = code(value, Code.YIELD_VALUE)
    if stack_effects[YIELD_VALUE][1]:
        code.POP_TOP()
    return r


nodetype()
def ListComp(body, code=None):
    if code is None:
        return body,
    code._tmp_level += 1
    try:
        temp = '_[%r]' % code._tmp_level
        code.BUILD_LIST(0)
        code.DUP_TOP()
        if sys.version<"2.4":
            code.LOAD_ATTR('append')
        code.STORE_FAST(temp)
        r = code(body)
        code.DELETE_FAST(temp)
    finally:
        code._tmp_level -= 1
    return r


nodetype()
def LCAppend(value, code=None):
    if code is None:
        return value,
    code.LOAD_FAST('_[%r]' % code._tmp_level)
    r = code(value)
    if sys.version<"2.4":
        code.CALL_FUNCTION(1)
        code.POP_TOP()
    elif sys.version>="2.7":    # ick
        code.LIST_APPEND(1)
        code.POP_TOP()
    else:
        code.LIST_APPEND()
    return r







nodetype()
def If(cond, then, else_=Pass, code=None):
    if code is None:
        return cond, then, else_
    else_clause = Label()
    end_if = Label()
    code(cond, else_clause.JUMP_IF_FALSE_OR_POP, then)
    if code.stack_size is not None:
        end_if.JUMP_FORWARD(code)
    code(else_clause, Code.POP_TOP, else_, end_if)

nodetype()
def Function(body, name='<lambda>', args=(), var=None, kw=None, defaults=(), code=None):
    if code is None:
        return body, name, ntuple(args), var, kw, tuple(defaults)
    c = code.nested(name, args, var, kw)
    c(body)
    if c.stack_size is not None:
        code.return_()
    c = c.code(code)
    if defaults:
        code(*defaults)
    if c.co_freevars:
        frees = c.co_freevars
        for name in frees:
            code.LOAD_CLOSURE(name)
        if sys.version>='2.5':
            code.BUILD_TUPLE(len(frees))
        code.LOAD_CONST(c)
        return code.MAKE_CLOSURE(len(defaults), len(frees))
    else:
        code.LOAD_CONST(c)
        return code.MAKE_FUNCTION(len(defaults))

def ntuple(seq):
    if isinstance(seq, basestring): return seq
    return tuple(map(ntuple, seq))




nodetype()
def Compare(expr, ops, code=None):
    if code is None:
        return fold_args(Compare, expr, tuple(ops))
    if len(ops)==1:
        op, arg = ops[0]
        code(expr, arg)
        return code.COMPARE_OP(op)
    fail = Label()
    finish = Label()
    code(expr)
    for op, arg in ops[:-1]:
        code(arg)
        code.DUP_TOP()
        code.ROT_THREE()
        code.COMPARE_OP(op)
        fail.JUMP_IF_FALSE_OR_POP(code)
    op, arg = ops[-1]
    code(arg)
    code.COMPARE_OP(op)
    finish.JUMP_FORWARD(code)
    fail(code)
    code.ROT_TWO()
    code.POP_TOP()
    return finish(code)


fast_to_deref = {
    LOAD_FAST: LOAD_DEREF,
    STORE_FAST: STORE_DEREF,
}

deref_to_deref = dict([(k,k) for k in hasfree])








nodetype()
def And(values, code=None):
    if code is None:
        return fold_args(And, tuple(values))
    end = Label()
    for value in values[:-1]:
        try:
            if const_value(value):
                continue        # true constants can be skipped
        except NotAConstant:    # but non-constants require code
            code(value, end.JUMP_IF_FALSE_OR_POP)
        else:       # and false constants end the chain right away
            return code(value, end)
    code(values[-1], end)

nodetype()
def Or(values, code=None):
    if code is None:
        return fold_args(Or, tuple(values))
    end = Label()
    for value in values[:-1]:
        try:
            if not const_value(value):
                continue        # false constants can be skipped
        except NotAConstant:    # but non-constants require code
            code(value, end.JUMP_IF_TRUE_OR_POP)
        else:       # and true constants end the chain right away
            return code(value, end)
    code(values[-1], end)

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

class Label(object):
    """A forward-referenceable location in a ``Code`` object"""

    __slots__ = 'backpatches', 'resolution'

    def __init__(self):
        self.backpatches = []
        self.resolution = None

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
        self.co_code = array('B')
        self.co_consts = [None]
        self.co_names = []
        self.co_varnames = []
        self.co_lnotab = array('B')
        self.emit = self.co_code.append
        self.blocks = []
        self.stack_history = []

    def emit_arg(self, op, arg):
        emit = self.emit
        if arg>0xFFFF:
            emit(EXTENDED_ARG)
            emit((arg>>16)&255)
            emit((arg>>24)&255)
        emit(op)
        emit(arg&255)
        emit((arg>>8)&255)

    def locals_written(self):
        vn = self.co_varnames
        hl = dict.fromkeys([STORE_FAST, DELETE_FAST])
        return dict.fromkeys([vn[arg] for ofs, op, arg in self if op in hl])




    def set_lineno(self, lno):
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
        return self.emit_arg(LOAD_CONST, arg)

    def CALL_FUNCTION(self, argc=0, kwargc=0, op=CALL_FUNCTION, extra=0):
        self.stackchange((1+argc+2*kwargc+extra,1))
        emit = self.emit
        emit(op); emit(argc); emit(kwargc)

    def CALL_FUNCTION_VAR(self, argc=0, kwargc=0):
        self.CALL_FUNCTION(argc,kwargc,CALL_FUNCTION_VAR, 1)    # 1 for *args

    def CALL_FUNCTION_KW(self, argc=0, kwargc=0):
        self.CALL_FUNCTION(argc,kwargc,CALL_FUNCTION_KW, 1)     # 1 for **kw

    def CALL_FUNCTION_VAR_KW(self, argc=0, kwargc=0):
        self.CALL_FUNCTION(argc,kwargc,CALL_FUNCTION_VAR_KW, 2) # 2 *args,**kw

    def BUILD_TUPLE(self, count):
        self.stackchange((count,1))
        self.emit_arg(BUILD_TUPLE,count)

    def BUILD_LIST(self, count):
        self.stackchange((count,1))
        self.emit_arg(BUILD_LIST,count)

    def UNPACK_SEQUENCE(self, count):
        self.stackchange((1,count))
        self.emit_arg(UNPACK_SEQUENCE,count)

    def RETURN_VALUE(self):
        self.stackchange((1,0))
        self.emit(RETURN_VALUE)
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
        def jump_target(offset):
            target = offset
            #print op
            #print hasjabs
            if op not in hasjabs:
                target = target - (posn+3)
                if target<0:
                    raise AssertionError("Relative jumps can't go backwards")
                if True:
                    target = offset - (posn+6)
            return target

        def backpatch(offset):
            target = jump_target(offset)
            #if target>0xFFFF:
            #    print hasjabs
            #    print hasjrel
            #    print op
            #    print "ofs: " + hex(offset) + ", tgt: " + hex(target) + ", posn: " + hex(posn)
                #exit(0)
                #raise AssertionError("Forward jump span must be <64K bytes")
            assert(op!=120)
            self.patch_arg(posn, 0x1FFFF, target,op)
            self.branch_stack(offset, old_level)

        if op==FOR_ITER:
            old_level = self.stack_size = self.stack_size - 1
            self.stack_size += 2
        else:
            old_level = self.stack_size
        self.stack_size -= (op in (JUMP_IF_TRUE_OR_POP, JUMP_IF_FALSE_OR_POP))
        posn = self.here()
        if arg is not None:
            print "jt: " + hex(jump_target(arg))
            self.emit_arg(op, jump_target(arg))
            self.branch_stack(arg, old_level)
            lbl = None
        else:
            self.emit_arg(op, 0x1FFFF)
            def lbl(code=None):
                backpatch(self.here())
        if op in (JUMP_FORWARD, JUMP_ABSOLUTE, CONTINUE_LOOP):
            self.stack_unknown()
        return lbl

    def COMPARE_OP(self, op):
        self.stackchange((2,1))
        self.emit_arg(COMPARE_OP, compares[op])

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

    decorate(classmethod)
    def from_function(cls, function, copy_lineno=False):
        code = cls.from_code(getattr(function, CODE), copy_lineno)
        return code


    decorate(classmethod)
    def from_code(cls, code, copy_lineno=False):
        import inspect
        self = cls.from_spec(code.co_name, *inspect.getargs(code))
        if copy_lineno:
            self.set_lineno(code.co_firstlineno)
            self.co_filename = code.co_filename
        self.co_freevars = code.co_freevars     # XXX untested!
        return self

    decorate(classmethod)
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
                print op
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

        return NEW_CODE(
            self.co_argcount, len(self.co_varnames),
            self.co_stacksize, flags, to_code(self.co_code),
            tuple(self.co_consts), tuple(self.co_names),
            tuple(self.co_varnames),
            self.co_filename, self.co_name, self.co_firstlineno,
            to_code(self.co_lnotab), self.co_freevars, self.co_cellvars
        )


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

compares = {}
for value, name in enumerate(cmp_op):
    compares[value] = value
    compares[name] = value
compares['<>'] = compares['!=']


for op in hasname:
    if not hasattr(Code, opname[op]):
        def do_name(self, name, op=op):
            self.stackchange(stack_effects[op])
            try:
                arg = self.co_names.index(name)
            except ValueError:
                arg = len(self.co_names)
                self.co_names.append(name)
            self.emit_arg(op, arg)
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
            try:
                arg = self.co_varnames.index(varname)
            except ValueError:
                arg = len(self.co_varnames)
                self.co_varnames.append(varname)
            self.emit_arg(op, arg)
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

generate_types = {
    int:        Code.LOAD_CONST,
    long:       Code.LOAD_CONST,
    bool:       Code.LOAD_CONST,
    CodeType:   Code.LOAD_CONST,
    str:        Code.LOAD_CONST,
    unicode:    Code.LOAD_CONST,
    complex:    Code.LOAD_CONST,
    float:      Code.LOAD_CONST,
    type(None): Code.LOAD_CONST,
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
    co_varnames = code.co_varnames
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
            def do_op(self,op=op,se=stack_effects[op]):
                self.stackchange(se); self.emit(op)

        setattr(Code, name, with_name(do_op, name))


















