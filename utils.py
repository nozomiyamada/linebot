import re
import pandas as pd

## LOAD DATA
DATA = pd.read_csv('data/beatles.csv', index_col='song') ## set song title as index 
DATA['lyrics'] = DATA['lyrics'].apply(lambda x: x.replace('<br>', '\n'))
SONGS = DATA.index  ## list of song title
ALBUM_YEAR = pd.read_csv('data/album_year.csv', index_col='album')['year'] ## pd.Series

## function to get Levenshtein distance between 2 strings
def levenshtein(str1, str2) -> int:
	str1 = '^' + str1
	str2 = '^' + str2
	distances = [list(range(len(str2)))]
	for i in range(1, len(str1)):
		row = [i]
		for j in range(1, len(str2)):
			insert = row[j-1] + 1
			delete = distances[i-1][j] + 1
			replace = distances[i-1][j-1] + int(str1[i]!=str2[j])
			row.append(min(insert, delete, replace))
		distances.append(row)
	return distances[-1][-1]

## function to tokenize English text
## full stop . is excluded as word boundary (due to song title)
def tokenize(text:str) -> set:
	## rough_token includes empty string ''
	rough_tokens = re.split(r'[\s;:,\-\(\)\"!?]', text.lower())
	tokens = set()  ## Bag of Words (i.e. order is ignored) 
	for token in rough_tokens:
		if token == '':
			continue
		if token.endswith("\'s"):
			tokens.add(token.replace("\'s", ''))  ## day's - > day
		if "\'" in token:
			tokens.add(token.replace("\'", ''))  ## don't -> dont
		tokens.add(token)
	return tokens

## function to remove whitespaces/punctuations
## e.g. A Hard Day's Night -> aharddaysnight
def remove_punct(text:str) -> str:
	return ''.join(c for c in text if c.isalnum()).lower()

## function to parse/encode query parameters and convert type
def parse_postback(postback:str) -> dict:
	"""
	"question=1&score=0&answer=Help!&correct=true"
	-> {'question': 1, 'score': 0, 'answer': 'Help!', 'correct': 'true'}
	"""
	result = {}
	for parameter in  postback.split('&'):
		key, value = parameter.split('=')
		try:
			result[key] = int(value)
		except:
			result[key] = value
	return result

def encode_postback(postback_dict:dict) -> str:
	return '&'.join(f'{key}={value}' for key, value  in postback_dict.items())

## create postback label : maximum 20 chrs 
def get_label(text:str) -> str:
	if len(text) > 20:
		return text[:19] + '…'
	else:
		return text