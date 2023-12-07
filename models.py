
# 'limit': token limit
# 'input': cost in dollars per 1,000 tokens of input
# 'output': cost in dollars per 1,000 tokens of output
# 'shutdown': date past which this is no longer usable
dictionary = {
'gpt-3.5-turbo':                {'mode':'chat',      'base':'gpt-3.5',   'instruct': True,   'limit': 4097,  'input': 0.0015, 'output': 0.0020,                       },
'gpt-3.5-turbo-0301':           {'mode':'chat',      'base':'gpt-3.5',   'instruct': True,   'limit': 4097,  'input': 0.0015, 'output': 0.0020,'shutdown':'2024-06-13'},
'gpt-3.5-turbo-0613':           {'mode':'chat',      'base':'gpt-3.5',   'instruct': True,   'limit': 4097,  'input': 0.0015, 'output': 0.0020,                       },
'gpt-3.5-turbo-1106':           {'mode':'chat',      'base':'gpt-3.5',   'instruct': True,   'limit': 16385, 'input': 0.0010, 'output': 0.0020,                       },
	# despite being non-16k, still has 16k token context window, though only 4k output
	# both 'gpt-3.5-turbo' and 'gpt-3.5-turbo-16k' will be pointed to this model on Dec 11 2023 
'gpt-3.5-turbo-16k':            {'mode':'chat',      'base':'gpt-3.5',   'instruct': True,   'limit': 16385, 'input': 0.0030, 'output': 0.0040,                       },
'gpt-3.5-turbo-16k-0613':       {'mode':'chat',      'base':'gpt-3.5',   'instruct': True,   'limit': 16385, 'input': 0.0030, 'output': 0.0040,                       },
'gpt-4':                        {'mode':'chat',      'base':'gpt-4',     'instruct': True,   'limit': 8192,  'input': 0.0300, 'output': 0.0600,                       },
'gpt-4-0314':                   {'mode':'chat',      'base':'gpt-4',     'instruct': True,   'limit': 8192,  'input': 0.0300, 'output': 0.0600,'shutdown':'2024-06-13'},
'gpt-4-0613':                   {'mode':'chat',      'base':'gpt-4',     'instruct': True,   'limit': 8192,  'input': 0.0300, 'output': 0.0600,                       },
'gpt-4-1106-preview':           {'mode':'chat',      'base':'gpt-4',     'instruct': True,   'limit': 128000,'input': 0.0100, 'output': 0.0300,                       },
'gpt-4-32k':                    {'mode':'chat',      'base':'gpt-4',     'instruct': True,   'limit': 32768, 'input': 0.0600, 'output': 0.1200,                       },
'gpt-4-32k-0314':               {'mode':'chat',      'base':'gpt-4',     'instruct': True,   'limit': 32768, 'input': 0.0600, 'output': 0.1200,'shutdown':'2024-06-13'},
'gpt-4-32k-0613':               {'mode':'chat',      'base':'gpt-4',     'instruct': True,   'limit': 32768, 'input': 0.0600, 'output': 0.1200,                       },                         
'gpt-3.5-turbo-instruct':       {'mode':'completion','base':'gpt-3.5',   'instruct': True,   'limit': 4097,  'input': 0.0015, 'output': 0.0020,                       },
'gpt-3.5-turbo-instruct-0914':  {'mode':'completion','base':'gpt-3.5',   'instruct': True,   'limit': 4097,  'input': 0.0015, 'output': 0.0020,                       },
'text-davinci-003':             {'mode':'completion','base':'gpt-3.5',   'instruct': True,   'limit': 4097,  'input': 0.0200, 'output': 0.0200,                       },
'text-davinci-002':             {'mode':'completion','base':'gpt-3.5',   'instruct': True,   'limit': 4097,  'input': 0.0200, 'output': 0.0200,                       },
'davinci-002':                  {'mode':'completion','base':'gpt-3 175B','instruct': False,  'limit': 16384, 'input': 0.0200, 'output': 0.0200,'shutdown':'2024-01-04'},
'babbage-002':                  {'mode':'completion','base':'gpt-3 1.3B','instruct': False,  'limit': 16384, 'input': 0.0005, 'output': 0.0005,'shutdown':'2024-01-04'},
'davinci-instruct-beta':        {'mode':'completion','base':'gpt-3 175B','instruct': True,   'limit': 2049,  'input': 0.0200, 'output': 0.0200,                       },
'curie-instruct-beta':          {'mode':'completion','base':'gpt-3 6.7B','instruct': True,   'limit': 2049,  'input': 0.0020, 'output': 0.0020,                       },
'text-davinci-001':             {'mode':'completion','base':'gpt-3 175B','instruct': True,   'limit': 2049,  'input': 0.0200, 'output': 0.0200,'shutdown':'2024-01-04'},
'text-curie-001':               {'mode':'completion','base':'gpt-3 6.7B','instruct': True,   'limit': 2049,  'input': 0.0020, 'output': 0.0020,'shutdown':'2024-01-04'},
'text-babbage-001':             {'mode':'completion','base':'gpt-3 1.3B','instruct': True,   'limit': 2049,  'input': 0.0005, 'output': 0.0005,'shutdown':'2024-01-04'},
'text-ada-001':                 {'mode':'completion','base':'gpt-3 350M','instruct': True,   'limit': 2049,  'input': 0.0004, 'output': 0.0004,'shutdown':'2024-01-04'},
'davinci':                      {'mode':'completion','base':'gpt-3 175B','instruct': False,  'limit': 2049,  'input': 0.0200, 'output': 0.0200,'shutdown':'2024-01-04'},
'curie':                        {'mode':'completion','base':'gpt-3 6.7B','instruct': False,  'limit': 2049,  'input': 0.0020, 'output': 0.0020,'shutdown':'2024-01-04'},
'babbage':                      {'mode':'completion','base':'gpt-3 1.3B','instruct': False,  'limit': 2049,  'input': 0.0005, 'output': 0.0005,'shutdown':'2024-01-04'},
'ada':                          {'mode':'completion','base':'gpt-3 350M','instruct': False,  'limit': 2049,  'input': 0.0004, 'output': 0.0004,'shutdown':'2024-01-04'},
'text-embedding-ada-002':       {'mode':'embedding', 'base':'cl100k',    'dimensions': 1536, 'limit': 8191,  'input': 0.00001,'output': 0.0000,                       },  
'text-similarity-ada-001':      {'mode':'embedding', 'base':'gpt-3',     'dimensions': 1024, 'limit': 2046,  'input': 0.0040, 'output': 0.0000,'shutdown':'2024-01-04'}, # Similarity
'text-similarity-babbage-001':  {'mode':'embedding', 'base':'gpt-3',     'dimensions': 2048, 'limit': 2046,  'input': 0.0050, 'output': 0.0000,'shutdown':'2024-01-04'},
'text-similarity-curie-001':    {'mode':'embedding', 'base':'gpt-3',     'dimensions': 4096, 'limit': 2046,  'input': 0.0200, 'output': 0.0000,'shutdown':'2024-01-04'},
'text-similarity-davinci-001':  {'mode':'embedding', 'base':'gpt-3',     'dimensions': 12288,'limit': 2046,  'input': 0.2000, 'output': 0.0000,'shutdown':'2024-01-04'},
'text-search-ada-doc-001':      {'mode':'embedding', 'base':'gpt-3',     'dimensions': 1024, 'limit': 2046,  'input': 0.0040, 'output': 0.0000,'shutdown':'2024-01-04'}, # Documents
'text-search-babbage-doc-001':  {'mode':'embedding', 'base':'gpt-3',     'dimensions': 2048, 'limit': 2046,  'input': 0.0050, 'output': 0.0000,'shutdown':'2024-01-04'},
'text-search-curie-doc-001':    {'mode':'embedding', 'base':'gpt-3',     'dimensions': 4096, 'limit': 2046,  'input': 0.0200, 'output': 0.0000,'shutdown':'2024-01-04'},
'text-search-davinci-doc-001':  {'mode':'embedding', 'base':'gpt-3',     'dimensions': 12288,'limit': 2046,  'input': 0.2000, 'output': 0.0000,'shutdown':'2024-01-04'},
'text-search-ada-query-001':    {'mode':'embedding', 'base':'gpt-3',     'dimensions': 1024, 'limit': 2046,  'input': 0.0040, 'output': 0.0000,'shutdown':'2024-01-04'}, # Queries
'text-search-babbage-query-001':{'mode':'embedding', 'base':'gpt-3',     'dimensions': 2048, 'limit': 2046,  'input': 0.0050, 'output': 0.0000,'shutdown':'2024-01-04'},
'text-search-curie-query-001':  {'mode':'embedding', 'base':'gpt-3',     'dimensions': 4096, 'limit': 2046,  'input': 0.0200, 'output': 0.0000,'shutdown':'2024-01-04'},
'text-search-davinci-query-001':{'mode':'embedding', 'base':'gpt-3',     'dimensions': 12288,'limit': 2046,  'input': 0.2000, 'output': 0.0000,'shutdown':'2024-01-04'},
'code-search-ada-text-001':     {'mode':'embedding', 'base':'gpt-3',     'dimensions': 1024, 'limit': 2046,  'input': 0.0040, 'output': 0.0000,'shutdown':'2024-01-04'}, # Text
'code-search-babbage-text-001': {'mode':'embedding', 'base':'gpt-3',     'dimensions': 2048, 'limit': 2046,  'input': 0.0050, 'output': 0.0000,'shutdown':'2024-01-04'},
'code-search-ada-code-001':     {'mode':'embedding', 'base':'gpt-3',     'dimensions': 1024, 'limit': 2046,  'input': 0.0040, 'output': 0.0000,'shutdown':'2024-01-04'}, # Code
'code-search-babbage-code-001': {'mode':'embedding', 'base':'gpt-3',     'dimensions': 2048, 'limit': 2046,  'input': 0.0050, 'output': 0.0000,'shutdown':'2024-01-04'},
'text-davinci-edit-001':        {'mode':'edit',                                                                                                'shutdown':'2024-01-04'},
'code-davinci-edit-001':        {'mode':'edit',                                                                                                'shutdown':'2024-01-04'},
'text-moderation-latest':       {'mode':'moderation','dead':False,                                                                                                    }, 
'text-moderation-stable':       {'mode':'moderation','dead':False,                                                                                                    },
		# setting 'dead' to False prevents these from being caught in the clearing out of models inaccessible to the user, 
		# since they're always accessible even though they don't display as such
'tts-1':                        {'mode':'speech'},
'tts-1-hd':                     {'mode':'speech'},
	# tts-1 is optimized for speed/real-time applications, tts-1-hd is optimized for quality
}
synonyms = {'ada-search-query': 'text-search-ada-query-001', 'babbage-search-query': 'text-search-babbage-query-001', 'curie-search-query': 'text-search-curie-query-001', 'davinci-search-query': 'text-search-davinci-query-001', 'ada-search-document': 'text-search-ada-doc-001', 'babbage-search-document': 'text-search-babbage-doc-001', 'curie-search-document': 'text-search-curie-doc-001', 'davinci-search-document': 'text-search-davinci-doc-001', 'ada-similarity': 'text-ada-similarity-001', 'babbage-similarity': 'text-babbage-similarity-001', 'curie-similarity': 'text-curie-similarity-001', 'davinci-similarity': 'text-davinci-similarity-001', 'ada-code-search-code': 'code-search-ada-code-001', 'babbage-code-search-code': 'code-search-babbage-code-001', 'ada-code-search-text': 'code-search-ada-text-001', 'babbage-code-search-text': 'code-search-babbage-text-001', 'tts-1-1106': 'tts-1', 'tts-1-hd-1106': 'tts-1-hd'}
'''
import re
compressedData = {
	'.*?edit.*$': {'mode': 'edit', 'shutdown': '2024-01-04'}, 
	'.*?moderation.*$': {'mode': 'moderation', 'dead': False},
	'mode': 'chat', 'base': 'gpt-3.5', 'instruct': True, 'limit': ('?','[db].*?2$',16384,4097), 'input': 0.0015, 'output': 0.0020,
	'gpt-(.*)$': {
		'3\.5-turbo(.*)': {
			'-instruct.*?': {'mode': 'completion'},
			'-16k.*': {'limit': 16385, 'input': .003, 'output': .004},
		},
		'4(.*)': {
			'base': 'gpt-4', 'limit': 8192, 'input': .03, 'output': .06,
			'-32k.*': {'limit': 32768, 'input': .06, 'output': .12}
		},
		'.*?-03.+': {'shutdown': '2024-06-13'}
	},
	'(?:text|code)-[es](.*)$' : {
		'mode': 'embedding', 'base': 'gpt-3', 'limit': 2046, 'output': 0, 'shutdown': '2024-01-04', 'instruct': None,
		'm.*': {'base': 'cl100k', 'dimensions': 1536, 'limit': 8191, 'input': .00001, 'shutdown': None},
		'[ie].*?-([abcd]).*': {
			'dimensions': ('=','12288 if x0=="d" else 2**("abc".index(x0)+10)',),
			'input': ('=',"[.004,.005,.02,.2]['abcd'.index(x0)]",)
		}
	},
	'(.*)': {
		'mode': 'completion', 'instruct': False, 'limit': 2049, 'output': 0, 'shutdown': '2024-01-04',
		'(?:text-)?([abcd]).*': {
			'base': ('=',"f\"{x1} {['350M','1.3B','6.7B','175B']['abcd'.index(x0)]}\"",'gpt-3'),
			'input': ('=',"[.0004,.0005,.002,.02]['abcd'.index(x0)]",),
			'output': ('=',"[.0004,.0005,.002,.02]['abcd'.index(x0)]",),
		},
		'(?:text-.*?(.)|(.*?-)beta)$': {
			'instruct': True, 
			'(?:([23])|.*?[^1](-))': {
				'shutdown': None, 
				'\\d': {'limit': 4097, 'base': 'gpt-3.5'}},
		},
		'[db].*?2$': {'limit': 16384}
	}
}
def decompress(test, data, lower = False): 
	D, dict, tuple, str = {}, type({}), type(()), type('')
	for (rx, y) in data.items(): 
		if type(y) not in [dict, tuple]: 
			D[rx] = y
		elif type(y) == tuple: 
			if y[0] == '=': 
				# '(.*?)-.*?': {'key': ('=','len(x1)**len(x0)+1','abc')} run on 'qq-88xa1' will return {'key': 10}
				# 	since the captured group evaluates to x0 = 'qq', and x1 is entered as 'abc'
				D[rx] = eval(f'lambda {",".join([f"x{k}" for k in range(len(y)-1)])}: '+y[1])(test, *y[2:])
			elif y[0]=='?': 
				D[rx] = (y[2] if re.fullmatch(y[1],test) else y[3])
			else: 
				D[rx] = (y[0])(test, *y[1:])
		elif m := re.fullmatch(rx, test): 
			test2 = (test if len(n := [x for x in m.groups() if x != None]) == 0 else n[0])
			D = {**D, **decompress(test2, y, True)}
			if rx[-1] == '$': 
				break
	return D if lower else {k: v for k, v in D.items() if v != None}
M = ['gpt-3.5-turbo', 'gpt-3.5-turbo-0301', 'gpt-3.5-turbo-0613', 'gpt-3.5-turbo-16k', 'gpt-3.5-turbo-16k-0613', 'gpt-4', 'gpt-4-0314', 'gpt-4-0613', 'gpt-3.5-turbo-instruct', 'gpt-3.5-turbo-instruct-0914', 'text-davinci-003', 'text-davinci-002', 'davinci-002', 'babbage-002', 'davinci-instruct-beta', 'curie-instruct-beta', 'text-davinci-001', 'text-curie-001', 'text-babbage-001', 'text-ada-001', 'davinci', 'curie', 'babbage', 'ada', 'text-embedding-ada-002', 'text-similarity-ada-001', 'text-similarity-babbage-001', 'text-similarity-curie-001', 'text-similarity-davinci-001', 'text-search-ada-doc-001', 'text-search-babbage-doc-001', 'text-search-curie-doc-001', 'text-search-davinci-doc-001', 'text-search-ada-query-001', 'text-search-babbage-query-001', 'text-search-curie-query-001', 'text-search-davinci-query-001', 'code-search-ada-text-001', 'code-search-babbage-text-001', 'code-search-ada-code-001', 'code-search-babbage-code-001', 'text-davinci-edit-001', 'code-davinci-edit-001', 'text-moderation-latest', 'text-moderation-stable']
Models2 = {}
for m in M: 
	Models2[m] = decompress(m, compressedData)
for i in Models2.keys(): 
	if Models[i] != Models2[i]: 
		print(i) 
		print(Models[i])
		print(Models2[i])
else: 
	print(Models2 == Models)
'''
