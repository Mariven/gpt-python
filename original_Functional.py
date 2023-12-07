from math import pi, e
import re
import copy
functionList = []

typeStringRegex = re.compile('')

__ = "__"


typeStringDict = {
	"product": "*", "coproduct": "+",
	"listLeft": "[", "listRight": "]",
	"hom": "->",
	"parenthesisLeft": "(", "parenthesisRight": ")"
	}
typeStringDictStr = {
	"product": ", ", "coproduct": " | ",
	"listLeft": "[", "listRight": "]",
	"hom": " -> ",
	"parenthesisLeft": "(", "parenthesisRight": ")"
	}
typeStringRegexDict = {
	"product": "\\*", "coproduct": "\\+",
	"listLeft": "\\[", "listRight": "\\]",
	"hom": "->",
	"parenthesisLeft": "\\(", "parenthesisRight": "\\)"
	}
verboseTypes = False

class FunctionalError(Exception):
	pass

class ValueStore:
	def __init__(self, mode, default = None, **kwargs):
		self.mode = mode
		self.values = {}
		for i in kwargs.keys():
			self.values[i] = kwargs[i]
		self.kwargs = kwargs
		self.default = default
	def fallbackReturn(self, key, *targets):
		for i in targets:
			if isinstance(i, ValueStore):
				try:
					return i.values[key]
					if type(i.default) in [type(self.__init__), type(lambda x: x)]:
						return i.default(key)
					return i.default

				except:
					pass
			elif isinstance(i, dict):
				try:
					return i[key]
				except:
					pass
			elif type(i) in [type(self.__init__), type(lambda x: x)]:
				try:
					return i(key)
				except:
					pass
			else:
				if i != None:
					return i
		raise FunctionalError("Fallback Return fell through on key " + key)
	def __call__(self, *args):
		return self.get(*args)
	def __getitem__(self, *args):
		return self.get(*args)
	def __setitem__(self, *args):
		self.modifyValue(args[0], args[1])



	def get(self, key, default = None):
		''' gets a value specified in the ValueStore's instantiation;
			if the value is not found, returns default specified in
			function call, falling back to key default and then
			instantiation default (possibly a function call)'''
		return self.fallbackReturn(key, self.values, default, self.default)
		if type(key) != str:
			key = str(key)
		try:
			return self.values[key]
		except:
			if default == None:
				if self.default == None:
					raise FunctionalError("Value not found: " + str(type(key)) + " " + str(key))
				else:
					if type(self.default) in [type(self.__init__), type(lambda x: x)]:
						return self.default(key)
					else:
						return self.default
			else:
				return default
	def modifyValue(self, key, value = None):
		if value != None:
			self.values[key] = value


prefixMode = ValueStore("prefix", "", labelR = ": ", position = "start")
infixMode = ValueStore("infix", "", position = "mid")
postfixMode = ValueStore("postfix", "", labelL = " | ", position = "end")
listMode = ValueStore("list", "", wrapL = "[", wrapR = "]", joiner = ", ")
tupleMode = ValueStore("list", "", wrapL = "(", wrapR = ")", joiner = ", ")

class AnnotatedTreeNode(ValueStore):
	def __init__(self, children = [], parent = None, label = "", labelType = "default"):
		self.label = label
		self.parent = parent
		if type(children) != list:
			children = [children]
		self.children = []
		self.addChildren(children)
		self.labelType = labelType
		if self.labelType == "default":
			self.getDefaultLabelType()
		try: 
			self.default = self.labelType.get
		except: 
			self.default = listMode.get
		self.values = {}
		self.valueDefaults = {}
		self.kwargs = {}
	def __str__(self):
		#wrapEach wraps each child in the L and R
		#joiner goes between each (wrapped) child
		#labelL/R go on the left and right of the label
		#position determines the label position
		if self.children == []:
			return self.label
		try: 
			mode = self.labelType.mode
		except: 
			mode = listMode.mode
		LT = self.labelType
		label = self.get("labelL") + str(self.label) + self.get("labelR")
		childrenCopy = [self.get("wrapEachL") + str(x) + self.get("wrapEachR") for x in self.children]
		p = self.get("position")
		if p == "mid" or p == "middle":
			p = len(childrenCopy)//2
		if isinstance(p, int):
			x = self.get("joiner").join(childrenCopy)
		else:
			x = "".join(childrenCopy)
		if p == "end":
			x = x + label
		if p == "start":
			x = label + x
		return self.get("wrapL") + x + self.get("wrapR")
	def getDefaultLabelType(self):
		#to be overwritten by subclasses
		self.labelType = listMode
	def addChild(self, child):
		self.children.append(child)
		if isinstance(child, AnnotatedTreeNode): 
			child.addParent(self)
	def addChildren(self, children):
		for i in children:
			self.addChild(i)
	def addParent(self, parent):
		#also to be overwritten
		self.parent = parent

class Type(AnnotatedTreeNode, ValueStore):
	def __add__(self,T2):
		return Type([copy.deepcopy(self), copy.deepcopy(T2)],
				 label=typeStringDictStr['coproduct'])

	def __mul__(self, T2):
		return Type([copy.deepcopy(self), copy.deepcopy(T2)],
				 label=typeStringDictStr['product'])

	def __gt__(self, T2): # > operator
		return Type([copy.deepcopy(self), copy.deepcopy(T2)],
				 label=typeStringDictStr['hom'])

	def __invert__(self): # ~ operator, for lists
		return Type([copy.deepcopy(self)], label=typeStringDictStr['listLeft']+typeStringDictStr['listRight'])

	def getDefaultLabelType(self):
		tsd = typeStringDict
		tsds = typeStringDictStr
		if verboseTypes:
			try:
				x = {tsds['product']: 'Prod', tsds['coproduct']: 'Coprod',
				 tsds['hom']: 'Hom'}[self.label]
			except:
				if self.label[0] == tsds['listLeft']:
					x = 'List'
				else:
					x = self.label
			self.label = x
			self.labelType = ValueStore(x, "", labelR = '(',
										position = "start", wrapR = ")",
										joiner = ", ")
		else:
			if self.label in [tsds['product'],
							  tsds['coproduct'],tsds['hom']]:
				self.labelType = ValueStore("infixType", "", position = "mid", joiner = self.label)
			elif self.label[0] == tsds['listLeft']:
				self.labelType = ValueStore("listType", "", wrapL = '[', wrapR = ']')
			else:
				self.labelType = ValueStore("unknownType", "", position = "start")

	def addParent(self, parent):
		bp = ["->", " -> ", "|", " | ", "*", "+", ", ", "[]"]
		self.parent = parent
		if self.children != [] and self.labelType.mode == "infixType":
			if bp.index(self.label) > bp.index(self.parent.label) or (self.parent.label == self.label and '->' in self.label):
				self.labelType.modifyValue("wrapL", value = "(")
				self.labelType.modifyValue("wrapR", value = ")")

	def __repr__(self):
		return str(self)




def insert(L, NL, I):
	LL = [x for x in L]
	I = sorted(I)
	if len(NL) != len(I):
		raise Exception("FunctionalError: insert: Different number of elements to insert and insertion indices")
	for i in range(len(I)):
		LL.insert(I[i], NL[i])
	return LL

class Fun:
	def __init__(self, fun, name = None, funType = None, minArgs = -1):
		self.name = name
		self.fun = lambda *args: fun(*args)
		self.type = funType
		if minArgs == -1:
			try:
				minArgs = fun.__code__.co_argcount
			except:
				try:
					minArgs = fun.minArgs
				except:
					minArgs = 1
		self.minArgs = minArgs
		functionList.append(self)

	def __call__(self, *args):
		if self.minArgs > 1 and len(args) == 1 and type(args[0]) == tuple:
			args = args[0]
		if __ in args:
			indices = [i for i, x in enumerate(args) if x == __]
			args = [x for x in args if x != __]
			return Fun(lambda *args2: self.fun(*insert(args, args2, indices)), minArgs = self.minArgs - 1)
		else:
			return self.fun(*args)
	def __getitem__(self, items):
		#[] has lower priority than (), but higher priority than *, +, ...
		# and f[a, b, c] is translated as f.__getitem__((a, b, c))
		if self.minArgs > 1:
			return([self.fun(*x) for x in items])
		else:
			return([self.fun(x) for x in items])
	def __mul__(self, g):
		if type(g) == list:
			return [self * x for x in g]
		if not isinstance(g, Fun):
			g = Fun(g)
		return Fun(lambda *args: self.fun(g(*args)))
	def __rmul__(self, f):
		if type(f) == list:
			return [x * self for x in f]
		if not isinstance(f, Fun):
			f = Fun(f)
		return Fun(lambda *args: f(self.fun(*args)))
	def __truediv__(self, g):
		#f/g = g*f
		return g * self
	def __rtruediv__(self, f):
		return self * f
		return g * self
	def __matmul__(self, L):
		#f @ L = Map(f)(L)
		if L == '__':
			return(Fun(lambda L: list(map(f, L)))) #mysterious use case
		return Fun(lambda L_: list(map(f, L_)))(L)
	def __add__(self, f):
		if not isinstance(f, Fun):
			f = Fun(f)
		return Fun(lambda *args: self.fun(*args) + f.fun(*args))
	def __sub__(self, f):
		if not isinstance(f, Fun):
			f = Fun(f)
		return Fun(lambda *args: self.fun(*args) + (-1)*f.fun(*args))
	def __xor__(self, n):
		if type(n) != int or n < 0:
			raise FunctionalError("Invalid function power")
		if n == 0:
			return Fun(lambda x: x)
		if n == 1:
			return self
		if n > 1:
			return self*(self^(n-1))
	def __repr__(self):
		name = 'Function'
		if self.name != None:
			name += ' \'' + self.name + '\''
		if self.type != None:
			name += ': ' + str(self.type)
		return name

Num = Type(label = 'Num')
Str = Type(label = 'Str')
Bool = Type(label = 'Bool')
A = Type(label='A')
B = Type(label='B')
C = Type(label='C')
FunFun = Fun(lambda f: Fun(f))
Apply = Fun(lambda x: Fun(lambda g: g(x)))

Is = Fun(lambda P: Fun(lambda x: P(x)), 'Is', (A > Bool) > A > Bool)
IfElse = Fun(lambda P, a, b: Fun(lambda x: a(x) if P(x) else b(x)),
		name = 'IfElse', funType = (C>Bool)*A*B > (C>(A+B)), minArgs = 3)

#Function composition
Comp = Fun(lambda f: Fun(lambda g: Fun(lambda *args: f(g(*args)))),
		   name = 'Composition', funType = (B>C)>((A>B)>(A>C)))
RComp = Fun(lambda g: Fun(lambda f: Fun(lambda *args: f(g(*args)))),
		   name = 'Composition', funType = (A>B)>((B>C)>(A>C)))
#Mapping
Map = Fun(lambda f: Fun(lambda L: list(map(f, L))),
		  name = 'Map', funType = (A>B)>((~A)>(~B)))

Zip = Fun(lambda a, b: list(zip(a, b)), name = 'Zip', funType = (~A)*(~B) > ~~(A*B), minArgs = 2)
#Combinator Generation
#Com = Fun(lambda L: IfElse(lambda L1: len(L1) == 1, lambda L1: L1[0], lambda L1: L1[0]((Map(Com)(L1[1:]))*))
def Com(L, F):
	if len(L) == 0:
		return
	if not isinstance(L[0], list):
		return L[0](*[x for x in Map(lambda X: Com(X, F))(L[1])])
	return Com([Com(L[0], F)] + [L[1:]], F)


def _count(a, b, dx):
	L, i = [], a
	while i <= b:
		L.append(i)
		i += dx
	return L
Count = Fun(_count, name = 'Count', funType = Num * Num * Num > ~Num, minArgs = 3)


Sum = Fun(lambda L: sum(L), 'Sum', ~Num>Num)
Id = Fun(lambda x: x, 'Identity', A>A)
Zero = Fun(lambda x: 0, 'Zero', A>Num)
E = {'*': Fun(lambda x, y: x * y, minArgs = 2),
	 'L*': Fun(lambda L: L[0] * L[1]),
	 '+': Fun(lambda x, y: x + y, minArgs = 2),
	 'L+': Fun(lambda L: L[0] + L[1]),
	 '**': Fun(lambda x, y: x**y, minArgs = 2),
	 'L**': Fun(lambda L: L[0] ** L[1])}
Add, Mul, Pow = E['+'], E['*'], E['**']
Pow = E['**']
Max = Fun(lambda L: max(L))
Min = Fun(lambda L: min(L))
List = Fun(lambda *args: list(args[0]) if len(args) == 1 else list(range(args[0], args[1])))

f = Fun(lambda x: x+1)
g = Fun(lambda x: 2*x)
h = Fun(lambda x, y, z: x + 100 * y + 10000 * z)
L = [3, 4, 5]
LL = [[6, 7, 8], [9, 10, 11]]

Assoc = Fun(lambda f: Fun(lambda L: [[l, f(l)] for l in L]), 'Associator',
			(A > B) > (~A > ~(A*B)))
 #e.g., Assoc(lambda x: 2*x)([3, 4, 5]) = [[3, 6], [4, 8], [5, 10]]


def fold(f, B, a0):
	for i in range(len(B)):
		a0 = f(a0, B[i])
	return a0
Fold = Fun(fold, "Fold", (((A*B)>A)*(~B))>A)
#e.g., Sum = Fold(lambda x, y: x + y, __, 0), Prod

if "__name__" == "__main__":
	pass
