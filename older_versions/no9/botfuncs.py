# -*- coding: utf-8 -*-
import re
from collections import Counter

from linebot.v3.messaging import (
	TextMessage, FlexMessage, QuickReply, QuickReplyItem,
	MessageAction, 
	FlexBubble, FlexBox, FlexText, FlexSpan
)

from utils import *

## CLASS FOR GET INFORMATION BY SONG TITLE
class _GetBySongTitle:
	def __init__(self, col_name, mode_prefix='', decorate=lambda x: x):
		self.data = DATA[col_name] ## pd.Series : index - song title
		self.prefix = mode_prefix
		self.decorate = decorate  ## function to add sth to reply message

	def get(self, query:str) -> list:
		songtitles = search_song_title(query)
		if len(songtitles) > 10:
			reply = 'Please try again with more specific words.'
			messages = [TextMessage(text=reply)]
		elif len(songtitles) == 0:  ## no candidate
			reply = 'NOT FOUND:\nPlease try again with different words.'
			messages = [TextMessage(text=reply)]
		elif len(songtitles) == 1:  ## only one candidate -> return URL
			songtitle = songtitles[0]
			reterieved = self.data[songtitle]  ## retrieve data
			if type(reterieved) != str: ## Null
				return [TextMessage(text='NO DATA')]
			reply = self.decorate(reterieved, songtitle)
			if type(reply) == str:
				messages = [TextMessage(text=reply)]
			else:
				messages = [FlexMessage(altText=songtitle, contents=reply)]
		else:
			quickreply = QuickReply(items=[])  ## instantiation 
			for song in songtitles:
				label = get_label(song) ## max characters : 20
				item = QuickReplyItem(action=MessageAction(label=label, text=self.prefix+song))
				quickreply.items.append(item)
			messages = [TextMessage(text='candidate songs:', quickReply=quickreply)]
		return messages

_GetYoutube = _GetBySongTitle(
	col_name='official_youtube',
	mode_prefix='',
	decorate=lambda youtubeID, songtitle: 'https://www.youtube.com/watch?v=' + youtubeID)  ## add YouTube URL
get_official_youtube = _GetYoutube.get

_GetLyrics = _GetBySongTitle(
	col_name='lyrics',
	mode_prefix='lyrics ',
	decorate=lambda lyrics, songtitle: create_flex_lyrics(lyrics, songtitle))
get_lyrics = _GetLyrics.get

_GetHarmony = _GetBySongTitle(
	col_name='harmony_youtube',
	mode_prefix='harmony ',
	decorate=lambda youtubeID, songtitle: 'https://www.youtube.com/watch?v=' + youtubeID)  ## add YouTube URL
get_harmony = _GetHarmony.get

_GetBass = _GetBySongTitle(
	col_name='bass_youtube',
	mode_prefix='bass ',
	decorate=lambda youtubeID, songtitle: 'https://www.youtube.com/watch?v=' + youtubeID)  ## add YouTube URL
get_bass = _GetBass.get

_GetBassTab = _GetBySongTitle(
	col_name='bass_tab',
	mode_prefix='basstab ',
	decorate=lambda songsterrURL, songtitle: songsterrURL + '?openExternalBrowser=1') 
get_basstab = _GetBassTab.get

_GetInfo = _GetBySongTitle(
	col_name='database_url',
	mode_prefix='info ',
	decorate=lambda databaseURL, songtitle: databaseURL)  
get_info = _GetInfo.get

##################################################

def create_flex_lyrics(lyrics, songtitle):
	## GET SONG INFO
	album = DATA.loc[songtitle, 'album']
	year = ALBUM_YEAR[album]
	if year >= 1967:
		color = '#0367D3' ## blue
	else:
		color = '#CB444A' ## red

	## PREPARE BUBBLE CONTAINER
	bubble_container = FlexBubble(size='giga')

	## ADD HEADER WITH SONG TITLE, ALBUM, YEAR
	song_title_text = FlexText(text=songtitle, color='#FFFFFF', size='xl', weight='bold')
	song_album_text = FlexText(text=f'{album} ({year})', color='#FFFFFF66', size='lg') 
	header_box = FlexBox(
		layout='vertical',
		contents=[song_title_text, song_album_text],
		spacing='sm',
		backgroundColor=color,
		paddingAll='xxl'
	)
	bubble_container.header = header_box

	## ADD EMPTY BOX TO BODY
	bubble_container.body = FlexBox(
		layout='vertical',
		spacing='xxl', ## space between each paragraph 
		contents=[]
	)

	## INSERT EACH LINE TO PARAGRAPH BOX
	## paragraphs = list of list of lines e.g [[Jojo was..., But he...], [Get Back, ...]]
	paragraphs = [paragraph.split('\n') for paragraph in lyrics.split('\n\n')]
	for paragraph in paragraphs:
		para_box = FlexBox(layout="vertical", contents=[], spacing='sm')
		for line in paragraph:
			para_box.contents.append(FlexText(text=line, size='lg', wrap=True))
		bubble_container.body.contents.append(para_box)

	return bubble_container


HOW_TO_USE = pd.read_csv('data/howtouse.csv')
HOW_TO_USE.fillna('', inplace=True)
def create_flex_howtouse():
	## PREPARE CONTAINER
	container = FlexBubble(size='mega')
	container.header = FlexBox(
		backgroundColor='#DDDDDD',
		layout='vertical',
		contents=[FlexText(text='How To Use', size='xl', color='#405195', weight='bold')]
	)
	container.body = FlexBox(layout='vertical', spacing='md', contents=[])

	## APPEND BODY CONTENT
	for _, row in HOW_TO_USE.iterrows():
		container.body.contents.append(FlexText(text=row['title'], weight='bold'))  ## title
		description_box = FlexBox(layout='horizontal', contents=[FlexText(text=' ', flex=1)])
		description_box.contents.append(FlexBox(
			layout='vertical',
			spacing='sm',
			flex=10,
			contents=[
				FlexText(wrap=True, contents=[
					FlexSpan(text=row['description']),
					FlexSpan(text=' ' + row['command'], color='#FF0000', style='italic')
				]),
				FlexBox(layout='horizontal', contents=[
					FlexText(flex=0, text='try: '),
					FlexText(
						text=row['example'],
						margin='sm',
						color='#3579F6',
						decoration='underline',
						action=MessageAction(text=row['example'])),
				])
			]
		))
		container.body.contents.append(description_box)
	return [FlexMessage(altText='How To Use', contents=container)]

##################################################

## CREATE INVERTED INDEX FOR SONG TITLE
## { token : {set of songs that contain the word} }
INVERTED_INDEX_songtitles= {'64': {"When I'm Sixty-Four"}}
for song in SONGS:
	for token in tokenize(song):
		INVERTED_INDEX_songtitles	[token] = INVERTED_INDEX_songtitles	.get(token, set()) | {song}

## FUNCTION TO FIND THE MOST SIMILAR SONG TITLE
def search_song_title(query:str, min_partial_len=4, distance_threshold=0.5) -> list:
	"""
	find song title from input text
	ambiguous matching ranked by
		1. exact match
		2. partial match (if only one song)
		3. token match - refer INVERTED_INDEX_songtitles	
		4. Levenshtein Distance

	output is LIST regardless of the number of matched songs (0 or more)
	"""
	query_lower = re.sub(r'\s\s+', ' ', query).strip().lower()  ## shrink space & lowercase 
	query_no_punct = remove_punct(query_lower)  ## a hard day's -> aharddays
	query_tokens = query_lower.split(' ')

	partial_match_songs = []
	min_distance = 1000
	min_distance_songs = []

	for song in SONGS:
		song_lower = song.lower()  ## lowercase song title
		song_no_punct = remove_punct(song)  ## remove punct 

		### EXACT MATCH ###
		if query_lower==song_lower or query_no_punct==song_no_punct:
			return [song]
		
		### PARTIAL MATCH - 4 chars or more ###
		if (query_lower in song_lower and len(query_lower) >= min_partial_len) or\
			(query_no_punct in song_no_punct and len(query_no_punct) >= min_partial_len):
			partial_match_songs.append(song)

		### LEVENSHTEIN DISTANCE ###
		if len(query_no_punct) < len(song_no_punct):  ##  
			window_len = len(query_no_punct)  
			distance = min(levenshtein(query_no_punct, song_no_punct[i:i+window_len])
				for i in range(0, len(song_no_punct)-window_len+1))
		else:	
			distance = levenshtein(query_no_punct, song_no_punct)

		if distance < min_distance and distance / len(query_no_punct) < distance_threshold:
			min_distance = distance
			min_distance_songs = [song]
		elif distance == min_distance and distance / len(query_no_punct) < distance_threshold:
			min_distance_songs.append(song)

	### NUM OF MATCHED TOKEN ###
	token_counter = Counter()
	for token in query_tokens:
		if token in INVERTED_INDEX_songtitles	:
			token_counter.update(INVERTED_INDEX_songtitles	[token])
			
	if len(token_counter) == 0:
		max_token_count, token_match_songs = 0, []
	else:
		max_token_count = token_counter.most_common()[0][1]
		token_match_songs = [song for song, count in token_counter.most_common() if count==max_token_count]
	
	## only one partial match
	if len(partial_match_songs) == 1:
		return partial_match_songs
	## if token match exists
	elif max_token_count >= 1:
		return token_match_songs
	## no token match AND multiple partial match
	elif len(partial_match_songs) >= 2:
		return partial_match_songs
	## else, minimum Levenshtein distance
	else:
		return min_distance_songs