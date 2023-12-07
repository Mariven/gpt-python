import re
import inspect

def getName(x, wrong = []):
	for y in reversed(inspect.stack()):
		if len(z := [k for k, v in y.frame.f_locals.items() if v is x and k not in wrong]) > 0: return z[0]
	return None

def idxInsert(L, NL, I):
	LL = [x for x in L]
	I = sorted(I)
	if len(NL) != len(I):
		raise ValueError("insert: Different number of elements to insert and insertion indices")
	for i in range(len(I)):
		LL.insert(I[i], NL[i])
	return LL

def metaWrap(f): 
	def g(*args): 
		for (i, x) in enumerate(args):
			if isinstance(x, Meta): 
				args[i] = x.func
		if isinstance(x, Meta): 
			return Meta(lambda x: f(x))
		else:
			return f(x)
	return g

class Meta: 
	'''
		Allows for symbolic variables that have indeterminate values but can still be used in expressions
			If x = Meta('x'), then (x + 2)**2 will evaluate to a Meta object with label '(x + 2)**2' and function lambda x: (x + 2)**2
			So if you let y = (x+2)**2, then y(3) will evaluate to (3 + 2)**2 = 25
		Meta objects are also treated as blanks by wrapped functions, so you can use them for partial evaluation
			E.g., if Zip is an Fn and x is a Meta, then Zip(x, [1, 2, 3]) is a function that takes ['a','b','c'] to [('a', 1), ('b', 2), ('c', 3)]
	'''
	def __init__(self, label, **kwargs):
		self.label = label 
		self.func = kwargs.get('func', lambda x: x)
		self.args = kwargs.get('args', 1)
		self.priority = kwargs.get('priority', 100)
		self.basic = kwargs.get('basic', True)
		self.vars = kwargs.get('basicvars', [self])
	def pr(self, priority): 
		# priority is used for parentheses in label combinations -- we want Mul(Add(x, y), z) to be (x+y)*z, not x+y*z
		# in general, a binary operator's label will parenthesize the operands if their priority is lower than the operator's priority
		if self.priority <= priority: 
			return '('+self.label+')'
		return self.label
	def __str__(self):
		return self.label
	def __repr__(self):
		return self.label
	def __call__(self, *args):
		return self.func(*args)
	def __abs__(self):
		return Meta(f'abs({self.label})', lambda *x: abs(self.func(*x)), self.args, 10)
	def _binop(self, other, symbol, function, reversed, pr):
		# general protocol for binary infix operators; reversed = True is for radd, rmul, etc., and pr is priority
		s1, args = self.pr(pr), self.args
		if isinstance(other, Meta):
			s2, args = other.pr(pr), args + other.args
			if reversed: 
				func = lambda *x: function(other.func(*(x[:other.args])), self.func(*(x[other.args:])))
			else:
				func = lambda *x: function(self.func(*(x[:self.args])), other.func(*(x[self.args:])))
			# if we have say z = (x + y) * x, then z.args will be 3 when it should be 2; need to fix
		else: 
			s2 = str(other)
			if reversed: 
				func = lambda *x: function(other, self.func(*x))
			else:
				func = lambda *x: function(self.func(*x), other)
		if reversed: 
			return Meta(f'{s2}{symbol}{s1}', func=Fn(func), args=args, pr=pr, basic=False)
		else:
			return Meta(f'{s1}{symbol}{s2}', func=Fn(func), args=args, pr=pr, basic=False)
	def _unop(self, symbol, function, pr):
		# general protocol for unary prefix operators
		s1, args = self.pr(pr), self.args
		return Meta(f'{symbol}{s1}', func=Fn(lambda *x: function(self.func(*x))), args=args, pr=pr, basic=False)
	def __invert__(self):
		return self._unop('~', lambda x: ~x, 7)
	def __neg__(self):
		return self._unop('-', lambda x: -x, 7)
	def __pos__(self):
		return self._unop('+', lambda x: +x, 7)
	def __ceil__(self):
		return self._unop('ceil', lambda x: ceil(x), 10)
	def __floor__(self):
		return self._unop('floor', lambda x: floor(x), 10)
	def __add__(self, other):
		return self._binop(other, '+', lambda a, b: a + b, False, 2)
	def __radd__(self, other):
		return self._binop(other, '+', lambda a, b: a + b, True, 2)
	def __mul__(self, other):
		return self._binop(other, '*', lambda a, b: a * b, False, 4)
	def __rmul__(self, other):
		return self._binop(other, '*', lambda a, b: a * b, True, 4)
	def __pow__(self, other):
		return self._binop(other, '**', lambda a, b: a ** b, False, 6)
	def __rpow__(self, other):
		return self._binop(other, '**', lambda a, b: a ** b, True, 6)
	def __truediv__(self, other):
		return self._binop(other, '/', lambda a, b: a / b, False, 3)
	def __rtruediv__(self, other):
		return self._binop(other, '/', lambda a, b: a / b, True, 3)
	def __floordiv__(self, other):
		return self._binop(other, '//', lambda a, b: a // b, False, 3)
	def __rfloordiv__(self, other):
		return self._binop(other, '//', lambda a, b: a // b, True, 3)
	def __sub__(self, other):
		return self._binop(other, '-', lambda a, b: a - b, False, 1)
	def __rsub__(self, other):
		return self._binop(other, '-', lambda a, b: a - b, True, 1)
	def __and__(self, other):
		return self._binop(other, '&', lambda a, b: a & b, False, 0.8)
	def __rand__(self, other):
		return self._binop(other, '&', lambda a, b: a & b, True, 0.8)
	def __or__(self, other):
		return self._binop(other, '|', lambda a, b: a | b, False, 0.6)
	def __ror__(self, other):
		return self._binop(other, '|', lambda a, b: a | b, True, 0.6)
	def __xor__(self, other):
		return self._binop(other, '^', lambda a, b: a ^ b, False, 0.7)
	def __rxor__(self, other):
		return self._binop(other, '^', lambda a, b: a ^ b, True, 0.7)
	def __matmul__(self, other):
		return self._binop(other, '@', lambda a, b: a @ b, False, 5)
	def __rmatmul__(self, other):
		return self._binop(other, '@', lambda a, b: a @ b, True, 5)
	def __mod__(self, other):
		return self._binop(other, '%', lambda a, b: a % b, False, 3)
	def __rmod__(self, other):
		return self._binop(other, '%', lambda a, b: a % b, True, 3)
	def __lshift__(self, other):
		return self._binop(other, '<<', lambda a, b: a << b, False, 1)
	def __rlshift__(self, other):
		return self._binop(other, '<<', lambda a, b: a << b, True, 1)
	def __rshift__(self, other):
		return self._binop(other, '>>', lambda a, b: a >> b, False, 1)
	def __rrshift__(self, other):
		return self._binop(other, '>>', lambda a, b: a >> b, True, 1)

class Fn:
	'''
		Function wrapper that allows for FP-like manipulations and partial evaluation (via Meta objects)
			Lots of galaxy-brained notation for function manipulation:
				- f * g is the composition f(g(x))
				- f @ L is the map of f over L, i.e., [f(x) for x in L]
				- ~f is the function that maps f, i.e. f @ -
				- f / g is the function that returns f(x) if that works, else g(x)
				- f // g is the function that returns f(x) if that works, else g as an object
				- -f is the function that returns f(*L) for L, i.e., turns a polyadic function into a monadic one
				- +f is the function that returns f(L) for L, i.e., turns a monadic function into a polyadic one
				- f ** n is the function that returns f(f(...(f(x))...)) for n iterations
				- f < D is the function that inserts D's values at the indicated keys, e.g. if f is tetradic, then f < {0: 'x', 3: 19} is the dyadic f('x', -, -, 19)
				- f <= D inserts D's values in place, so f itself becomes the dyadic function
	'''
	# function wrapper for functional programming-style syntactic sugar
	def __init__(self, fn, domType = None, codType = None, name = None):
		if isinstance(fn, Fn):
			# the function being wrapped should not be a wrapper itself, but maybe there'll be a point to re-wrapping
			self.fn = fn.fn
		else: 
			self.fn = fn
		self.type = type
		self.__name__ = name
		self.domType, self.codType = domType, codType
		if domType == None: 
			self.domType = '?'
		if codType == None:
			self.codType = '?'
		if self.__name__ == None:
			self.__name__ = getName(fn, ['fn', 'self'])
		if self.__name__ == None: 
			self.__name__ = getName(self, ['fn', 'self'])
		if self.__name__ == None: 
			self.__name__ = '<unnamed>'
	def ensure_Fn(f): 
		# need to expand this to include callables in general, and to deal with non-callables 
		# (e.g., lists -- should we wrap them as constant functions?)
		def wrapper(self, other): 
			if not isinstance(other, Fn): 
				other = Fn(other)
			return f(self, other)
		return wrapper

	def __call__(self, *args, **kwargs):
		if [isinstance(x, Meta) for x in args].count(True) > 0:
			indices = [i for i, x in enumerate(args) if isinstance(x, Meta)]
			args = [x for x in args if not isinstance(x, Meta)]
			return Fn(lambda *args2: self.fn(*idxInsert(args, args2, indices)))
		else: 
			return self.fn(*args, **kwargs)
	
	def __str__(self): 
		s = 'function'
		if self.__name__ != '<unnamed>':
			s += ' ' + self.__name__
		if self.domType != '?' or self.codType != '?':
			s += ': ' + ('('+str(self.domType)+')' if '->' in self.domType else str(self.domType)) + ' -> ' + ('('+str(self.codType)+')' if '->' in self.codType else str(self.codType))
		return s

	@ensure_Fn
	def __mul__(self, other):
		# (f*g)(x) = f(g(x))
		def newfun(*args, **kwargs):
			return self.fn(other.fn(*args, **kwargs))
		return Fn(newfun) 

	@ensure_Fn
	def __rmul__(self, other):
		# (g*f)(x) = g(f(x))
		return self*other

	def __matmul__(self, other):
		# f @ L = map(f)(L) = [f(x) for x in L]
		def newfun(iterable):
			return [self.fn(x) for x in iterable]
		return Fn(newfun)

	def __invert__(self):
		# ~f(L) = map(f)(L) = [f(a) for a in L]
		def newfun(iterable):
			return [self.fn(e) for e in iterable]
		return Fn(newfun)

	@ensure_Fn
	def __truediv__(self, other):
		# (f/g)(x) = f(x) if that works, else g(x)
		# if g can't be called, then g is returned instead of g(x)
		if callable(other): 
			def newfun(*args, **kwargs):
				try: 
					return self.fn(*args, **kwargs)
				except: 
					return other(*args, **kwargs)
		else: 
			def newfun(*args, **kwargs):
				try: 
					return self.fn(*args, **kwargs)
				except: 
					return other
		return Fn(newfun)

	def __rtruediv__(self, other):
		# (g/f)(x) = g(x) if that works, else f(x)
		# but if g is non-callable, just return it as is (so there's really no point)
		if callable(other): 
			@ensure_Fn
			def newfun(*args, **kwargs):
				try: 
					return other(*args, **kwargs)
				except: 
					return self.fn(*args, **kwargs)
		else: 
			def newfun(*args, **kwargs):
				return g
		return Fn(newfun)

	def __floordiv__(self, other):
		# (f//g)(x) = f(x) if that works, else g as an object (not g(x))
		def newfun(*args, **kwargs):
			try: 
				return self.fn(*args, **kwargs)
			except: 
				return other
		return Fn(newfun)
	def __rfloordiv__(self, other): 
		# (g//f)(x) = g(x) if that works, else f
		def newfun(*args, **kwargs):
			try: 
				return other(*args, **kwargs)
			except: 
				return self
		return Fn(newfun)
	
	def __neg__(self):
		# (-f)(*L) = f(L). we turn a polyadic function into a monadic one, hence the minus sign
		# Note: function calls have higher priority than negation, so we can't do `f = Fn(sum); -f(2, 3, 4)`, 
		# because Python wants to call f *then* negate the result, but that just calls sum(2, 3, 4), which is an error
		# so we have to either define f as `-Fn(sum)` or call it as `(-f)(2, 3, 4)`.
		def newfun(*args):
			return self.fn(args)
		return Fn(newfun)
	
	def __pos__(self):
		# (+f)(L) = f(*L). monadic into polyadic, hence + 
		def newfun(arglist):
			return self.fn(*arglist)
		return Fn(newfun)
	
	def __pow__(self, n): 
		# repeats a function n times, with n=0 yielding the identity
		# Note: Python will apparently interpret an integer as a function before an exponent, so
		# f**3(5) has to be written as (f**3)(5) to prevent it from trying to interpret `3(5)`
		if n == 0: return Id
		if n == 1: return self
		if n == 2: return self*self
		# let's lower the recursion depth?
		if n % 2 == 0: 
			return (self**2)**(n//2)
		else: 
			return self*(self**(n-1))
		# if you want to iterate a wrapped *polyadic* function like f(a, b) = [a+b, a-b]
		# make it monadic first, iterate, and then make the result polyadic: g = (-(+f)**n); g(3, 4)

	# def __lt__(self, other):
	# 	# galaxy-brained partial application notation
	# 	# if we have an n-adic function f, and a dictionary D with keys in [0, ..., n-1]
	# 	# then the syntax `f < D ` inserts D's values at the respective argument indices
	# 	# e.g., if we have a tetradic f(a, b, c, d), then `f < {0: 'x', 3: 19} ` is the dyadic f('x', b, c, 19).   
	# 	if not isinstance(other, dict):
	# 		raise ValueError("Must provide a dictionary for < operation")
	# 	def newfun(*args, **kwargs):
	# 		print(args, other)
	# 		unassigned = list(range(len(args)+len(other)))
	# 		newargs = [None for x in unassigned]
	# 		for k, v in other.items():
	# 			newargs[k] = v
	# 			unassigned.remove(k)
	# 		for i in range(len(unassigned)): 
	# 			newargs[unassigned[i]] = args[i]
	# 		return self.fn(*newargs, **kwargs)
	# 	return Fn(newfun)

	# def __le__(self, other):
	# 	# like the above, but does it in place, so f itself becomes the dyadic function
	# 	self = self < other
	# 	return self

maxResolve = 4
def getType(x, maxResolve = maxResolve): 
	# wrapped types (Dict, List, Tuple) can allow for detailed type information
	# e.g., [[7, 8, 9], {'a': 1, 'b': 2}] returns type [[int], {str: int}]; it's not really a Python type, but a collection that bottoms out in Python types
	# for technical reasons, it actually returns a string, but parseTypeString can turn it into a collection
	# Type is the function that does this automatically, so Type([[7, 8, 9], {'a': 1, 'b': 2}])[0][0](1.4) returns 1
	# maxResolve is the maximum number of types that can be resolved before we just call it Any
	# e.g. [1, [1], [[1], 'a']] has type [int, [int], [[int], str]] so long as maxResolve >= 3, otherwise it's [Any]
	try: 
		return x.type(maxResolve)
	except:
		try: 
			return x.type()
		except: 
			if type(x) not in superTypeDict:
				return type(x).__name__
	if type(x) in superTypeDict:
		return superTypeDict[type(x)](x).type(maxResolve)

def getLiteralType(x): 
	try: 
		return x.literalType()
	except:
		if type(x) not in superTypeDict:
			return type(x)
	if type(x) in superTypeDict:
		return superTypeDict[type(x)](x).literalType()

def returnsuper(f): 
	def g(x): 
		if type(x) in superTypeDict:
			x = superTypeDict[type(x)](x)
		if type(y := f(x)) in superTypeDict:
			return superTypeDict[type(y)](y)
		else:
			return y
	return g

class Dict(dict):
	'''
		Wrapper for dictionaries that allows for more functionality and integration with Fn
			Allows for attribute-like access to keys, e.g. D.x is equivalent to D['x'] (as in JS and Lua)
			The operator * treats the dictionary as a function from keys to values, so (D * f)[k] = D[f(k)] and (f * D)[k] = f(D[k])
	'''
	# conceptually, we might think of a dictionary as... 
	# - a function from keys (the domain) to values (the range)
	# - a list of pairs (key, value)
	# - a list of items with associated data
	# - a collection of labeled subsets of the codomain
	# 
	def __init__(self, d={}):
		for k, v in d.items():
			if type(v) in superTypeDict:
				d[k] = superTypeDict[type(v)](v)
		super(Dict, self).__init__(d)
		self.__dict__ = self
	def filter(self, P): # only keeps k such that P(k, self[k])
		if len(self) == 0:
			return Dict({})
		# figure out arity of P
		if (arity := P.__code__.co_argcount) == 1: 
			return Dict({k: v for k, v in self.items() if P(k)})
		return Dict({k: v for k, v in self.items() if P(k, v)})
	def map(self, f): # applies f to each value in self
		return Dict({k: f(v) for k, v in self.items()})
	def mapKeys(self, f): # applies f to each key in self
		return Dict({f(k): v for k, v in self.items()})
	def __mul__(self, f): 
		return self.map(f)
	def __rmul__(self, f):
		return self.mapKeys(f)
	# general idea being: f * D applies f to keys, D * f applies f to values 
	def type(self, maxResolve = maxResolve): 
		D1 = {getType(k, maxResolve): [] for k in self}
		D2 = {getType(v, maxResolve): [] for v in self.values()}
		for k, v in self.items():
			D1[getType(k, maxResolve)].append(getType(v, maxResolve))
			D2[getType(v, maxResolve)].append(getType(k, maxResolve))
		D1 = {k: sorted(list(set(v))) for k, v in D1.items()}
		D2 = {k: sorted(list(set(v))) for k, v in D2.items()}
		E1, E2 = {}, {}
		for (a, b) in [(D1, E1), (D2, E2)]:
			for k in a: 
				if len(a[k]) <= maxResolve:
					b[k] = ", ".join(a[k])
				else:
					b[k] = "Any"
		if min([len(E1), len(E2)]) > maxResolve: 
			return "{Any"+": "+"Any}"
		if len(E1) > maxResolve: # so len(E2) <= maxResolve
			return "{Any: " + ", ".join(sorted([getType(x, maxResolve) for x in E2]))+"}" 
		if len(E2) > maxResolve:
			return "{" + ", ".join(sorted([getType(x, maxResolve) for x in E1])) + ": Any}"
		s = ''
		for i in sorted(E1.keys()): 
			s += i + ": "+E1[i] + ", "
		return "{" + s[:-2] + "}"
	@returnsuper
	def literalType(self): 
		D1 = {}
		for k, v in self.items():
			if (tk := getLiteralType(k)) not in D1.keys(): 
				D1[tk] = []
			if (tv := getLiteralType(v)) not in D1[tk]: 
				D1[tk].append(tv)
		for k in D1: 
			if len(D1[k]) == 1:
				D1[k] = D1[k][0]
			else:
				D1[k] = sorted(D1[k], key=lambda x: str(x))
		return D1

class List(list):
	def __init__(self, l=[]):
		for i, v in enumerate(l):
			if type(v) in superTypeDict:
				l[i] = superTypeDict[type(v)](v)
		super(List, self).__init__(l)
	def __getattr__(self, attr):
		if attr == 'head': 
			if len(self) == 0:
				raise ValueError('head of empty list')
			return self[0]
		elif attr == 'tail':
			return List(self[1:])
		elif attr == 'last':
			if len(self) == 0:
				raise ValueError('last of empty list')
			return self[-1]
		elif attr == 'init':
			return List(self[:-1])
		else: 
			return getattr(list, attr)
	@returnsuper
	def map(self, f):
		return list(map(f, self))
	@returnsuper
	def filter(self, f):
		return List(list(filter(f, self)))
	def type(self, maxResolve = maxResolve): 
		L = sorted(list(set([getType(x, maxResolve) for x in self])))
		n = len(L)
		if n == 0 or n > maxResolve: 
			return "[Any]"
		else: 
			return "[" + ", ".join(L) + "]"
	@returnsuper
	def literalType(self): 
		L = sorted(list(set([getLiteralType(x) for x in self])),key=str)
		n = len(L)
		if n == 0: 
			return []
		else: 
			return L

class Tuple(tuple):
	def __init__(self, t=[]):
		if type(t) != list:
			t = list(t)
		for i, v in enumerate(t):
			if type(v) in superTypeDict:
				t[i] = superTypeDict[type(v)](v)
		super(Tuple, self).__init__(t)
	@returnsuper
	def map(self, f):
		return Tuple(list(map(f, self)))
	@returnsuper
	def filter(self, f):
		return Tuple(list(filter(f, self)))
	def type(self):
		return ' x '.join([getType(x, maxResolve) for x in self])
	def literalType(self):
		return ' x '.join([getLiteralType(x) for x in self])

class Cn: 
	def __init__(self, collection, kind = None): 
		self.collection = collection
		if kind == None: 
			self.kind = 'Collection'
	def __str__(self): 
		if kind == 'Collection': 
			return 'Col('+', '.join([str(x) for x in self.collection])+')'
		if kind == 'Pair': 
			return 'Pair('+str(self.collection[0])+', '+str(self.collection[1])+')'
		if kind == 'Function': 
			return 'Fun('+str(self.collection[0])+' -> '+str(self.collection[1])+')'

def parseTypeString(s): 
	while s[0] == ' ': s = s[1:]
	while s[-1] == ' ': s = s[:-1]
	depths = {'(': 0, '[': 0, '{': 0}
	pairs = {')': '(', ']': '[', '}': '{'}
	point, blocks = 0, []
	if s[0] == '[' and s[-1] == ']': # not the correct way to do this
		return List([parseTypeString(s[1:-1])])
	elif s[0] == '(' and s[-1] == ')':
		return Tuple([parseTypeString(s[1:-1])])
	elif s[0] == '{' and s[-1] == '}': 
		return Dict({parseTypeString(s[1:-1].split(':')[0]): parseTypeString(s[1:-1].split(':')[1])})
	if ',' not in s and '->' not in s: 
		try: 
			return strTypeDict[s]
		except: 
			if re.fullmatch('[a-zA-Z0-9_]+', s) != None: 
				return s
			else: 
				raise ValueError(f'invalid type string {s}')
	for i in range(len(s)):
		if s[i] in depths.keys(): 
			depths[s[i]] += 1
		elif s[i] in pairs.keys():
			depths[pairs[s[i]]] -= 1
		if s[i] == ',' and all([depths[x] == 0 for x in depths.keys()]):
			blocks.append(s[point:i])
			point = i+1
	blocks.append(s[point:])
	blocks = [x for x in blocks if len(x) > 0]
	return [parseTypeString(s) for s in blocks]

def Type(x): 
	return parseTypeString(getType(x))[0]

FFn = Fn(lambda f: Fn(f))
Apply = Fn(lambda f, *args: f(*args), '(A -> B) x A', 'B', 'Apply')

Comp = Fn(lambda f, g: Fn(lambda *args: f(g(*args))), '(B -> C) x (A -> B)', 'A -> C', 'Comp')
RComp = Fn(lambda f, g: Fn(lambda *args: f(g(*args))), '(A -> B) x (B -> C)', 'A -> C', 'RComp')
Map = Fn(lambda f, L: list(map(f, L)), '(A -> B) x [A]', '[B]', 'Map')
Filter = Fn(lambda f, L: list(filter(f, L)), '(A -> Bool) x [A]', '[A]', 'Filter')
Zip = Fn(lambda a, b: list(zip(a, b)), '[A] x [B]', '[(A, B)]', 'Zip')
Id = Fn(lambda x: x)

function = type(lambda x: x)
strTypeDict = {'dict': dict, 'list': list, 'tuple': tuple, 'float': float, 'int': int, 'str': str}
superTypeDict = {dict: Dict, list: List, tuple: Tuple, function: Fn}

'''
Type display names: 
	function (domain A, codomain B): A -> B
		right-associative, so A -> B -> C is A -> (B -> C), not (A -> B) -> C
	list of A: [A]
	dictionary A -> B: {A: B}
'''