
from utils import *
import random

from linebot.v3.messaging import (
	TextMessage, QuickReply, QuickReplyItem,
	PostbackAction, FlexMessage, FlexBubble, FlexBox, FlexText
)

def create_lyrics_quiz():
	selected_song = DATA.drop(index=['Flying', 'Revolution 9'])['lyrics'].sample(4)
	answer_title = selected_song.index[0]
	wrong_titles = selected_song.index[1:]
	selected_song_tokens = selected_song[0].split()
	token_length = random.randint(5, 9)
	start_token_index = random.randint(0, len(selected_song_tokens)-token_length)
	partial_lyrics = ' '.join(selected_song_tokens[start_token_index:start_token_index+token_length])
	
	return partial_lyrics.lower(), answer_title, wrong_titles

def create_postback_reply(postback):
	postback_dict = parse_postback(postback)
	postback_dict['question'] += 1

	reply_bubble = FlexBubble()

	## HEADER 
	if postback_dict['answer'] == 'NONE':  ## first question
		reply_bubble.header =FlexBox(
			layout='vertical',
			contents = [FlexText(text='Lyrics Quiz Start!')]
		)
	else:
		answer_text = FlexText(text=f'Answer : {postback_dict["answer"]}', wrap=True) ## the answer of previous question
		if postback_dict['correct'] == 'true':
			correct_or_not = FlexText(text='Correct!', weight='bold', color='#55BB36') ## green
		else:
			correct_or_not = FlexText(text='Wrong!', weight='bold', color='#CB444A') ## red
		reply_bubble.header = FlexBox(
			layout = 'vertical',
			contents = [answer_text, correct_or_not] 
		)

	## make quick reply items
	if postback_dict['question'] <= 5:
		partial_lyrics, answer_title, wrong_titles = create_lyrics_quiz()
		postback_dict['answer'] = answer_title
		postback_dict['correct'] = 'false'
		quickreply_buttons = []
		## add wrong answer
		for title in wrong_titles:
			label = get_label(title)
			item = QuickReplyItem(action=PostbackAction(label=label, displayText=title, data=encode_postback(postback_dict)))
			quickreply_buttons.append(item)

		## add correct answer
		postback_dict['score'] += 1
		postback_dict['correct'] = 'true'
		label = get_label(answer_title)
		item = QuickReplyItem(action=PostbackAction(label=label, displayText=answer_title, data=encode_postback(postback_dict)))
		quickreply_buttons.append(item)

		## shuffle items
		quickreply = QuickReply(items=random.sample(quickreply_buttons, 4))

		## body and footer
		reply_bubble.body = FlexBox(
			layout='vertical',
			backgroundColor='#EEEEEE',
			paddingAll='xs',
			contents=[FlexText(text=f'QUESTION {postback_dict["question"]} :', size='lg', weight='bold', align='center')]
		)
		reply_bubble.footer = FlexBox(
			layout='vertical',
			contents=[FlexText(text=partial_lyrics, wrap=True, align='center')]
		)
		return [FlexMessage(altText='Lyrics Quiz', contents=reply_bubble, quickReply=quickreply)]
	else:
		## body and footer
		reply_bubble.body = FlexBox(
			layout='vertical',
			backgroundColor='#EEEEEE',
			paddingAll='xs',
			contents=[FlexText(text=f'SCORE : {postback_dict["score"]} / 5', size='xl', weight='bold', align='center')]
		)
		result_message = {
			5: 'You are the true Beatlemania!',
			4: 'Close! Just a little more!',
			3: 'You are an ordinary fan',
			2: 'Study more about The Beatles',
			1: 'Please Help Me!',
			0: 'Paul is crying'
		}[postback_dict['score']]

		reply_bubble.footer = FlexBox(
			layout='vertical',
			contents=[FlexText(text=result_message, wrap=True, weight='bold', align='center')]
		)
		return [FlexMessage(altText=f'SCORE : {postback_dict["score"]} / 5', contents=reply_bubble)]