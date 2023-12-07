import inspect

def recdir(x, showModules = False, seenKeys=[], levelsRemaining = 1): 
	D = {}
	for k in dir(x): 
		if k in seenKeys: 
			continue
		seenKeys.append(k)
		try: 
			v = getattr(x, k)
		except AttributeError:
			continue
		except ModuleNotFoundError as e:
			print("ModuleNotFoundError: {}".format(e))
			continue
		if not inspect.isclass(v) and not inspect.ismodule(v) and not k.startswith('_'): 
			try: 
				D[k] = str(inspect.signature(v))
			except: 
				D[k] = type(v)
		if inspect.isclass(v) or (inspect.ismodule(v) and showModules):
			D[k] = recdir(v, showModules, seenKeys, levelsRemaining - 1) if levelsRemaining > 0 else '...'
	return D

def profile(dcs): 
	# takes a list of dictionaries and extracts commonalities shared by all dictionaries, to save space
	# recursing into both lists and other dictionaries
	data, keyList, keyListList, keyDicList, badKeys = {}, [], [], [], []
	for dc in dcs: 
		for k,v in dc.items(): 
			if type(v) == dict and k not in keyDicList: 
				keyDicList.append(k)
			elif type(v) == list and k not in keyListList: 
				keyListList.append(k)
			elif type(v) not in [dict, list] and k not in keyList: 
				keyList.append(k)
	for k in keyList: 
		if (k in keyListList or k in keyDicList) and (k not in badKeys): 
			badKeys.append(k)
	for K in [(keyList, lambda x: type(x) not in [list, dict]), (keyListList, lambda x: type(x) == list), (keyDicList, lambda x: type(x) == dict)]: 
		for k in K[0]: 
			for dc in dcs: 
				if (k not in dc.keys() or not K[1](dc[k])) and (k not in badKeys): 
					badKeys.append(k)
	for bk in badKeys: 
		for K in [keyList, keyListList, keyDicList]: 
			K = [k for k in K if k != bk]
	keyVals = {k: [] for k in keyList}
	for k in keyList: 
		for dc in dcs: 
			if dc[k] not in keyVals[k]: 
				keyVals[k].append(dc[k])
	for k, v in keyVals.items(): 
		if len(v) == 1:
			data[k] = v[0]
			for dc in dcs: 
				dc.pop(k)
	keyValLens = {k: [] for k in keyListList}
	for k in keyListList: 
		for dc in dcs: 
			if len(dc[k]) not in keyValLens[k]: 
				keyValLens[k].append(len(dc[k]))
	for k, v in keyValLens.items(): 
		if len(v) == 1:
			data[k] = []
			for n in range(v[0]): 
				typeList = []
				for i in range(len(dcs)): 
					if type(dcs[i][k][n]) not in typeList: 
						typeList.append(type(dcs[i][k][n]))
				if len(typeList) == 1 and typeList[0] == dict: 
					recurse = []
					for i in range(len(dcs)): 
						recurse.append(dcs[i][k][n])
					recurse, new_data = profile(recurse)
					data[k].append(new_data)
					for i in range(len(dcs)): 
						dcs[i][k][n] = recurse[i] 
	for k in keyDicList: 
		recurse = []
		for i in range(len(dcs)): 
			recurse.append(dcs[i])[k]
		recurse, new_data = profile(recurse)
		data[k] = new_data
		for i in range(len(dcs)): 
			dcs[i][k] = recurse[i]
	return dcs, data