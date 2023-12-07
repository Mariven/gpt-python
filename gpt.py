from auxiliary import *
from supertypes import *
import tiktoken, openai
import os, re, ast, json, datetime, pytz
import tabulate, requests
from models import dictionary as Models
from models import synonyms as ModelSynonyms

openai.api_key = open("api_key.txt", "r").read()

Models = Dict(Models)

# b/c OpenAI will add models and deprecate others in the future, check diff between models.py and list of available models
# won't update the models.py automatically, though, since they don't programmatically make the values (price per token, etc.) available; have to do it manually

permittedModels = [model['id'] for model in openai.Model.list().to_dict_recursive()['data']]
modelDelta = [[], []] # first is available but unlisted, second is listed but unavailable
for model in permittedModels:
	if model not in Models.keys() and model not in ModelSynonyms.keys(): 
		modelDelta[0].append(model)
for model, params in Models.items():
	if 'shutdown' in params and datetime.datetime.now() > datetime.datetime.strptime(params['shutdown'], '%Y-%m-%d'): # if the model is deprecated or manually deactivated
		if 'dead' not in params: # if params['dead'] exists and is False, it's manually kept alive
			params['dead'] = True
	elif model not in permittedModels:
		if 'dead' not in params: 
			params['dead'] = True
for model in [model for model, params in Models.items() if 'dead' in params and params['dead']]: 
	Models.pop(model)
	modelDelta[1].append(model)

print('Checking available models against listed models')
if (l1 := len(modelDelta[0])) > 0: 
	print(' -- ' + str(l1) + ' model' + 's'*(l1 > 1) + ' available but unlisted (' + ', '.join(sorted(modelDelta[0]))+')')
if (l2 := len(modelDelta[1])) > 0: 
	print(' -- ' + str(l2) + ' model' + 's'*(l2 > 1) + ' listed but unavailable (' + ', '.join(sorted(modelDelta[1]))+')')

Settings = Dict({
	'modes': ['chat', 'completion', 'embedding', 'edit', 'moderation'], # ordered by primacy; chat is default
	'chat': {
		'parameters': {
			'messages', 'model', 'max_tokens', 'stream', 'stop', 
			'temperature', 'top_p', 'n', 
			'frequency_penalty', 'presence_penalty', 
			'function_call', 'functions', 'logit_bias', 'user'
		},
		'required': {'model', 'messages',},
		'defaults': {'model': 'gpt-4-0613', 'max_tokens': None},
		'function': openai.ChatCompletion.create, 
		'endpoint': 'https://api.openai.com/v1/chat/completions',
	}, 
	'completion': {
		'parameters': {
			'prompt', 'model', 'max_tokens', 'stream', 'stop', 
			'temperature', 'top_p', 'best_of', 'n', 
			'frequency_penalty', 'presence_penalty', 
			'echo','logit_bias','logprobs', 'suffix', 'user',
		},
		'defaults': {'model': 'gpt-3.5-turbo-instruct', 'max_tokens': 500, 'logprobs': None},
		'required': {'model', 'prompt',},
		'function': openai.Completion.create, 
		'endpoint': 'https://api.openai.com/v1/completions',
	},
	'embedding': {
		'parameters': {
			'model', 'input',
		},
		'required': {'model', 'input',},
		'defaults': {'model': 'text-embedding-ada-002', 'max_tokens': None},
		'function': openai.Embedding.create, 
		'endpoint': 'https://api.openai.com/v1/embeddings',
	},
	'edit': {
		'parameters': {
			'model', 'input', 'instruction', 'temperature', 'n', 'top_p',
		},
		'defaults': {'model': 'text-davinci-edit-001'},
		'required': {'model', 'instruction'}, # input defaults to ''
		'function': openai.Edit.create,
		'endpoint': 'https://api.openai.com/v1/edits',
	},
	'moderation': {
		'parameters': {
			'model', 'input',
		},
		'required': {
			'input', # model defaults to text-moderation-latest
		},
		'defaults': {'model': 'text-moderation-latest'},
		'function': openai.Moderation.create,
		'endpoint': 'https://api.openai.com/v1/moderations',
	},
	'defaults': {
		'max_tokens': 500, 
		'temperature': 0.4, 
		'stream': False,
		'chat': {'model': 'gpt-4-0613',},
		'completion': {'model': 'gpt-3.5-turbo-instruct','logprobs': 5,},
		'embedding': {'model': 'text-embedding-ada-002',},
		'edit': {'model': 'text-davinci-edit-001',},
		'moderation': {'model': 'text-moderation-latest',}
	},
})
		

# the variables are capitalized to pretend they're enums; the actual strings ought to stay lowercase
System, User, Assistant, Undefined, Function = 'system', 'user', 'assistant', 'undefined', 'function'

def showAvailableModels(table = False): 
	modelList0 = openai.Model.list()
	modelList = modelList0.to_dict_recursive()['data']
	shorterModelList, commonalities = profile(modelList)
	for i in shorterModelList: 
		# convert the unix timestamps to mm/dd/yyyy, and remove the root key, which happens to always equal the id
		i['created'] = datetime.datetime.fromtimestamp(i['created']).strftime('%m/%d/%Y')
		i['permission'][0]['created'] = datetime.datetime.fromtimestamp(i['permission'][0]['created']).strftime('%m/%d/%Y')
		i.pop('root')
	f = lambda x: sum([(z[0] in x)*z[1] for z in [['-4',-1000],['-3.5',-600],['instruct',-100],['davinci',-301],['curie',-100],['003',-30],['002',-20],['001',-10],['-0',5],['text',-30],['ada',100]]])
	if(table): 
		print(tabulate.tabulate(sorted([[x["id"]]+[x['permission'][0]['allow_'+z] for z in ['sampling','logprobs','search_indices','view']] for x in shorterModelList], key = lambda x: f(x[0])), headers = ['model','sampling','logprobs','search_indices','view'], showindex="always", tablefmt="github"))
	else: 
		print(", ".join(sorted([x["id"] for x in shorterModelList], key = f))+'\n')

class Message: 
	def __init__(self, **kwargs): 
		# identify role, setting to Undefined if unable to
		self.data, self.role, self.content = kwargs, None, None
		if self.role == None: 
			# if the role wasn't recognized and no content was provided, interpret the role argument as containing the content
			if content == None: 
				self.role, self.content = Undefined, role
				return
			else: 
				# but if the role wasn't recognized and content *was* provided, something's gone wrong
				raise KeyError(f"Role not recognized: {s}")
		# by now, self.role will always have been defined
		if isinstance(content, Message): 
			# then make this like the given Message but with the new role
			self.content = content.content
			return
	def __str__(self): 
		return f'({self.role}, "{self.content}")'
	__repr__ = __str__
	def format(self, roleSuggest = None): 
		D = {'role': self.role.lower(), 'content': self.content}
		if self.role == Undefined and roleSuggest in [None, Undefined]: 
			print(f"Warning: No role given or suggested for the message: '{str(self)}'. Defaulting to User.")
			D['role'] = User.lower()
		return D
	def tokenCount(self, tokenizer): 
		n = tokenizer(self.content)
		if self.role != Undefined: 
			n += tokenizer(self.role)
		return n + 4 # the extra four comes from the way the API formats each message for GPT's use 

class Dialogue(list): 
	def __init__(self, messages, **kwargs): 
		super(Dialogue, self).__init__(messages)
		self.list, self.data = [], kwargs
		for msg in messages: 
			if not isinstance(msg, Message): 
				# it better have been either a string or a (role, content) pair
				try: 
					if type(msg) == str: 
						self.list.append(Message(msg))
					else: 
						self.list.append(Message(*msg))
				except: 
					raise ValueError(f"Could not recognize message: {msg}. Is it of the form (role, content)?")
			else: 
				self.list.append(msg)
	def __str__(self): 
		return "["+', '.join([str(msg) for msg in self.list])+"]"
	__repr__ = __str__
	def __add__(self, other): 
		# so we can do Dialogue + Dialogue and Dialogue + Message
		if isinstance(other, Dialogue): 
			return Dialogue(self.list + other.list)
		elif isinstance(other, Message): 
			return Dialogue(self.list + [other])
	def __radd__(self, other): 
		# so we can do Message + Dialogue
		if isinstance(other, Message): 
			return Dialogue([other] + self.list)
	def format(self, roleRule = None): 
		messages = []
		roleList, n = [msg.role for msg in self.list], len(self.list)
		if Undefined in roleList:
			if roleRule == None:  
				print(f"Warning: Undefined roles given with no rule to provide them for Dialogue: '{str(self)}'. Defaulting to defaulting as User.")
				roleRule = lambda L: [User if x.lower() == Undefined.lower() else x for x in L]
			roleList = roleRule(roleList)
			if len(roleList) != n: 
				raise ValueError(f"Role rule {roleRule} gave a different number of roles than were given in the dialogue: {str(self)}!")
		for i in range(n): 
			messages.append(self.list[i].format(roleList[i]))
		return {'messages': messages}
	def __getitem__(self, n): 
		return self.list[n]
	def __iter__(self): 
		return self.list
	def __len__(self): 
		return len(self.list)
	def tokenCount(self, tokenizer): 
		return sum([msg.tokenCount(tokenizer) for msg in self.list])

class Text: 
	def __init__(self, content, **kwargs): 
		self.content, self.data = content, kwargs
	def __str__(self): 
		return self.content
	__repr__ = __str__
	def tokenCount(self, tokenizer): 
		n = tokenizer([len(self.data['instruction']) if 'instruction' in self.data.keys() else 0])
		return n + tokenizer(self.content) # some number should be added to this, but idk what
	def format(self, mode, **kwargs): 
		term = {'completion': 'prompt', 'chat': 'content', 'moderation': 'input', 'embedding': 'input', 'edit': 'input'}[mode]
		if mode in ['moderation', 'embedding', 'completion']: 
			return {term: self.content}
		if mode == "chat":
			d = {term: self.content}
			if 'role' in kwargs:
				d['role'] = kwargs['role']
			elif 'role' in self.data:
				d['role'] = self.data['role']
			else: 
				raise ValueError(f"Role not provided for chat input: {self.content}")
			if 'name' in kwargs:
				d['name'] = kwargs['name']
			elif 'name' in self.data:
				d['name'] = self.data['name']
			if d['role'] == 'function' and 'name' not in d.keys(): 
				raise ValueError(f"Function role given without name: {self.content}")
			return d
		if mode == "edit": 
			if 'instruction' in kwargs:
				return {term: self.content, 'instruction': kwargs['instruction']}
			elif 'instruction' in self.data: 
				return {'input': self.content, 'instruction': self.data['instruction']}
			else: 
				raise ValueError(f"Instruction not provided for edit input: {self.content}")
				# we *could* just set it to its default '' here, but why bother? interested parties can set it explicitly

class GPT: 
	def __init__(self, **settings):
		autofixes = {'gpt4': 'gpt-4', 'complete': 'completion', 'embed': 'embedding', 'moderate': 'moderation', 'editor': 'edit', 'editing': 'edit', 'gpt35': 'gpt-3.5-turbo', 'gpt3.5': 'gpt-3.5-turbo', 'gpt-3.5': 'gpt-3.5-turbo', 'turbo': 'gpt-3.5-turbo', '16k': 'gpt-3.5-turbo-16k', 'turbo-16k': 'gpt-3.5-turbo-16k', 'turbo16k': 'gpt-3.5-turbo-16k', 'instruct': 'gpt-3.5-turbo-instruct', 'turbo-instruct': 'gpt-3.5-turbo-instruct'}
		if 'mode' in settings.keys() and settings['mode'].lower() in autofixes.keys():
				settings['mode'] = autofixes[settings['mode'].lower()]
		if 'mode' not in settings.keys() and 'model' not in settings.keys():
			raise ValueError(f"You must provide either a mode or a model for the GPT object.")
		# two levels of setting priority: global settings (the Settings dict) < local settings (the settings argument)gs
		# just implement the first then the second overwriting the first
		if 'model' in settings.keys(): # models *have* to be made mode-specific, though
			if settings['model'] not in Models:
				raise ValueError(f"Model {settings['model']} not recognized. Must be one of {Utility.reverse.keys()}.")
			modelMode = Models[settings['model']]['mode']
			if ('mode' in settings.keys() and settings['mode'] != modelMode): 
				raise ValueError(f"Model {settings['model']} Mode and model are inconsistent between local and global settings")
			settings['mode'] = modelMode
			self.settings = {'mode': modelMode}
		else: 
			self.settings = {'mode': settings['mode']}
			self.settings['model'] = Settings[self.settings['mode']]['defaults']['model']
		params = Settings[self.settings['mode']]['parameters']
		# generic default settings
		for par, val in Settings['defaults'].items(): 
			if par in params and val != None: 
				self.settings[par] = val
		for par, val in Settings[self.settings['mode']]['defaults'].items(): 
			if par in params: 
				self.settings[par] = val
		# generic object settings
		for par, val in settings.items(): 
			if par in params: 
				# let val = None overwrite too, so that we can use it to disable global defaults
				self.settings[par] = val
		for par in [par for par, val in self.settings.items() if val == None]: 
			self.settings.pop(par)
		try: 
			self.encoding = tiktoken.encoding_for_model(self.settings['model']) 
		except: 
			self.encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')
		self.tokenizer = lambda x: len(self.encoding.encode(x))
		call_methods = {
			'edit': lambda input, instruction, settings={}: run(input, settings, instruction=instruction), 
			'completion': lambda prompt, settings={}: run(prompt, settings),
			'embedding': lambda input, settings={}: run(input, settings), 
			'moderation': lambda input, settings={}: run(input, settings),
			'chat': lambda content, role="user", settings={}: run(input, settings, role=role)
		}
		call_method = call_methods[self.settings['mode']]
		self.__call__ = call_method
		self.response_history = []
		self.conversation = []
		if 'showFunctionUse' in settings.keys(): 
			self.showFunctionUse = settings['showFunctionUse']
		else:
			self.showFunctionUse = False
	def addMessage(self, content, role): 
		self.conversation.append({'role': role, 'content': content})
	def run(self, input, settings = {}, dry_run = False, **kwargs):
		if input == None: 
			return self.settings.copy()
		if type(input) == str: 
			input = Text(input, **kwargs)
		fullDict = self.settings.copy()
		if self.settings['mode'] != 'chat': 
			fullDict.update(input.format(self.settings['mode'], **kwargs))
		else: 
			self.conversation += [input.format(self.settings['mode'], **kwargs)]
			fullDict["messages"] = self.conversation
		fullDict.update(settings)
		if dry_run: 
			return fullDict
		else: 
			try: 
				response = self.dispatchDict(fullDict)
			except Exception as e: 
				self.response_history.append([fullDict, e])
				raise e
			self.response_history.append([fullDict, response])
			response = response.to_dict_recursive()
		return self.getContent(response)
	def dispatchDict(self, fullDict): 
		mode = fullDict['mode']
		fullDict.pop('mode')
		response = Settings[mode]['function'](**fullDict)
		return response
	def countTokens(self, input): 
		if type(input) == str: 
			return self.tokenizer(input)
		return input.tokenCount(self.tokenizer)
	def getContent(self, r): # gets content from overcomplicated response dictionary
		if r['object'] == 'text_completion': 
			return r['choices'][0]['text']
		if r['object'] == 'embedding': 
			return r["embedding"]
		if r['object'] == 'list': 
			return r['data'][0]['embedding']
		if r['object'] == 'edit':
			return r['choices'][0]['text']
		if r['object'] == 'moderation':
			return [k for k, v in r['results']["categories"].items() if v in ['true', True, 'True']]
		if r['object'] == 'chat.completion': 
			if r["choices"][0]["finish_reason"] == "function_call": 
				self.conversation.append({"role": r["choices"][0]["message"]["role"], "content": r["choices"][0]["message"]["content"], "function_call": r["choices"][0]["message"]["function_call"]})
				try: 
					name = r["choices"][0]["message"]["function_call"]["name"]
					arguments = json.loads(r["choices"][0]["message"]["function_call"]["arguments"])
					content = str(self.function_calls[name](**arguments))
				except: 
					raise ValueError(f"Function call {name} with arguments {arguments} failed.")
				if self.showFunctionUse:
					print("[called function {} with arguments {} and got response {}]".format(name, arguments, content))
				self.response_history.append("[called function {} with arguments {} and got response {}]".format(name, arguments, content))
				return self.run(content, {"functions": self.functions}, role="function", name=name)
			elif r["choices"][0]["finish_reason"] == "stop": 
				self.conversation.append({"role": r["choices"][0]["message"]["role"], "content": r["choices"][0]["message"]["content"]})
				return r["choices"][0]["message"]["content"]
	__call__ = run

def calc(e): 
	z = {}
	exec(f'from math import *\nr=lambda f:lambda x:1/f(x)\nln,cot,csc,sec=log,r(tan),r(sin),r(cos)\nz = '+e,z)
	return z['z']
functions_short = {
	'calc': (calc, 'An arithmetical expression, written in Python notation. Allows all standard mathematical operators and multi-line Python programs', {'required string e': '.'}), # lol
	'date': (lambda tz=False: datetime.datetime.now(pytz.timezone(tz) if tz else pytz.UTC).strftime('%H:%M:%S %Z, %a %b %d %Y'), 'The current date and time.', {'string tz': 'The timezone to use (example: US/Pacific). Defaults to UTC.'}),
}

def add(name, description, parameters): 
	dict = {
		'name': name,
		'description': description,
		'parameters': {'type': 'object', 'properties': {}, 'required': []},
	}
	for key, value in parameters.items():
		key = key.split()
		if len(key) == 2: 
			type, key, required = key[0], key[-1], False
		elif len(key) == 3:
			type, key, required = key[1], key[-1], True
		dict['parameters']['properties'][key] = {'type': type, 'description': value}
		if required: 
			dict['parameters']['required'].append(key)
	return dict
functions = []
function_calls = {}
for name, (function, description, parameters) in functions_short.items(): 
	dict = add(name, description, parameters)
	functions.append(dict)
	function_calls[name] = function

z='''
Functions to implement: 
- Run python code (w/ newlines)
- Run a shell command
- Wikipedia search (w/ summarization depending on context length & page length)
- Open a URL (same summarization protocol)
- Call a secondary chat instance with a given system message and user prompt
- Google search (top ten names, descriptions, URLs)
Some examples of implementations: 
	https://github.com/muellerberndt/mini-agi/blob/main/commands.py
		(memorize_thoughts, execute_python, execute_shell, web_search)
'''

Chatbot = GPT(model = 'gpt-4', showFunctionUse = True)
Chatbot.functions = functions
Chatbot.function_calls = function_calls
Completebot = GPT(mode="completion")
Embedbot = GPT(mode="embedding")
Editbot = GPT(mode="edit")
Moderatebot = GPT(mode="moderation")

edit = lambda input, instruction, settings={}: Editbot.run(input, settings, instruction=instruction)
completion = lambda prompt, settings={}: Completebot.run(prompt, settings)
embedding = lambda input, settings={}: Embedbot.run(input, settings)
moderation = lambda input, settings={}: Moderatebot.run(input, settings)
chat = lambda content, role="user", settings={}: Chatbot.run(content, settings, role=role)


if __name__ == "__main__": 
	sys_prompt = ['You have access to functions that calculate mathematical expressions and provide the date and time, though they are disabled by default to lower token usage. Should you need them to answer the user\'s question, send the message !enable and they will then appear for your use.', 'system']
	L, n = [GPT(model = 'gpt-4', showFunctionUse = True)], 0
	chat = lambda content, role="user", settings={}: L[n].run(content, settings, role=role)
	L[n].functions = functions
	L[n].function_calls = function_calls
	L[n].addMessage(*sys_prompt)
	while True: 
		i = str(input(f'({n}) > '))
		prefix = lambda p: lambda i: (True if i[len(p):] == '' else i[len(p):]) if i[:len(p)] == p else False
		if e := prefix('!eval ')(i): 
			print(eval(e))
			continue
		if prefix('!new')(i):
			L.append(GPT(model = 'gpt-4', showFunctionUse = True))
			n = len(L)-1
			L[n].functions = functions
			L[n].function_calls = function_calls
			L[n].addMessage(*sys_prompt)
			chat = lambda content, role="user", settings={}: L[n].run(content, settings, role=role)
			continue
		if e := prefix('!goto ')(i):
			if int(e) >= len(L): 
				print(f'Maximum chat number is {len(L)-1}. Use `!new` to open and move to a new chat.')
			else: 
				n = int(e)
				chat = lambda content, role="user", settings={}: L[n].run(content, settings, role=role)
			continue
		# use "[date, calc] blah blah blah" to give GPT those functions
		if re.search(r'\[([a-zA-Z0-9_, ]+)\]', i): 
			settings = {'functions': [z for z in L[n].functions if z['name'] in [x for x in re.search(r'\[([a-zA-Z0-9_, ]+)\]', '[date]').group(1).replace(' ','').split(',') if x in [y['name'] for y in L[n].functions]]]}
			i = i[i.index(']')+1:]
			if i[0] == ' ': 
				i = i[1:]
		else: 
			settings = {}
		x = chat(i, "user", settings)
		if '!enable' in x: 
			print('[GPT has enabled function use...]')
			print(chat('','user',{'functions': L[n].functions}))
		else:
			print(x)
