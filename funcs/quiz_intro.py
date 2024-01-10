
from funcs.utils import *
import random,  urllib

from linebot.v3.messaging import (
	TextMessage, QuickReply, QuickReplyItem, StickerMessage, AudioMessage,
	PostbackAction, FlexMessage, FlexBubble, FlexBox, FlexText
)

##################################################

## function to get part of lyrics and other 3 choices
def create_intro_quiz(previous_answers=None, level=1, num_choices=4):
	songs_to_drop = [] 
	if previous_answers != None:
		songs_to_drop += previous_answers  ## exclude previous answer
	selected_song = INTRO[INTRO.level <= level].drop(index=songs_to_drop).sample(num_choices)
	answer_title = selected_song.index[0]  ## correct answer 
	wrong_titles = selected_song.index[1:]  ## wrong answers
	duration = selected_song['duration'].values[0]
	answer_song_url = f"https://github.com/nozomiyamada/linebot/raw/main/data/intro/{urllib.parse.quote(answer_title)}.mp3"
	
	return answer_song_url, answer_title, wrong_titles, duration

def create_introquiz_postback(postback):
	postback_dict = parse_postback(postback)

	## START INTRO QUIZ - SELECT LEVEL
	if postback_dict['level'] == 0:
		quickreply = QuickReply(items=[])
		for level in range(1, 5):
			label = {1:'beginner', 2:'normal', 3:'hard', 4:'god'}[level]
			postback_dict['level'] = level
			if level == 4:
				postback_dict['num'] = 10
			item = QuickReplyItem(action=PostbackAction(label=label, displayText=label, data=encode_postback(postback_dict)))
			quickreply.items.append(item)
		return [TextMessage(text='select level', quickReply=quickreply)]
	
	postback_dict['question'] += 1 ## present question number + 1
	reply_bubble = FlexBubble()

	## HEADER - display previous answer
	if postback_dict['answer'] == 'NONE': ## first question
		reply_bubble.header =FlexBox(
			layout='vertical',
			contents = [FlexText(text='Intro Quiz Start!')]
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
	if postback_dict['question'] <= postback_dict['num']: ## present question No. <= total num
		level = postback_dict['level']
		num_choices = {1:4, 2:4, 3:5, 4:6}[level]

		if postback_dict['answer'] == 'NONE': ## first question
			answer_song_url, answer_title, wrong_titles, duration = create_intro_quiz(None, level, num_choices)
		else:
			answer_song_url, answer_title, wrong_titles, duration = create_intro_quiz(postback_dict['asked'], level, num_choices) ## drop previous answer
		
		postback_dict['answer'] = answer_title  ## update answer song
		postback_dict['asked'].append(answer_title)
		quickreply_buttons = []
		
		## add wrong answer button
		postback_dict['correct'] = 'false'
		for title in wrong_titles:
			label = get_label(title)
			item = QuickReplyItem(action=PostbackAction(label=label, displayText=title, data=encode_postback(postback_dict)))
			quickreply_buttons.append(item)

		## add correct answer button
		postback_dict['score'] += 1 
		postback_dict['correct'] = 'true'
		label = get_label(answer_title)
		item = QuickReplyItem(action=PostbackAction(label=label, displayText=answer_title, data=encode_postback(postback_dict)))
		quickreply_buttons.append(item)

		## shuffle button items
		quickreply = QuickReply(items=random.sample(quickreply_buttons, len(quickreply_buttons)))

		## BODY - display question No.
		reply_bubble.footer = FlexBox(
			layout='vertical',
			backgroundColor='#EEEEEE',
			paddingAll='xs',
			contents=[FlexText(text=f'QUESTION {postback_dict["question"]} :', size='lg', weight='bold', align='center')]
		)

		## FOOTER - lyrics
		# reply_bubble.footer = FlexBox(
		# 	layout='vertical',
		# 	contents=[FlexText(text=partial_lyrics, wrap=True, align='center')]
		# )
		return [
			FlexMessage(altText='Intro Quiz', contents=reply_bubble),
			AudioMessage(originalContentUrl=answer_song_url, quickReply=quickreply, duration=int(duration))
		]
	
	## after question 5 -> show result
	else:
		## BODY - total score
		reply_bubble.body = FlexBox(
			layout='vertical',
			backgroundColor='#EEEEEE',
			paddingAll='xs',
			contents=[FlexText(text=f'SCORE : {postback_dict["score"]} / {postback_dict["num"]}', size='xl', weight='bold', align='center')]
		)

		## FOOTER - evaluation message
		if postback_dict['num'] == 5:
			result_evaluation = {
				5: 'You are a good fan!',
				4: 'Close! Just a little more!',
				3: 'You are an ordinary fan',
				2: 'Study more about The Beatles',
				1: 'Please Help Me!',
				0: 'Paul is crying'
			}[postback_dict['score']]
		else:
			result_evaluation = {
				10: 'You are the true Beatlemania!',
				9: 'Close! Just a little more!',
				8: 'Close! Just a little more!',
				7: 'You\'re a good fan',
				6: 'You\'re a good fan',
				5: 'You are an ordinary fan',
				4: 'You are an ordinary fan',
				3: 'Study more about The Beatles',
				2: 'Study more about The Beatles',
				1: 'Please Help Me!',
				0: 'Paul is crying'
			}[postback_dict['score']]
			
		reply_bubble.footer = FlexBox(
			layout='vertical',
			contents=[FlexText(text=result_evaluation, wrap=True, weight='bold', align='center')]
		)
		messages = [FlexMessage(altText=f'SCORE : {postback_dict["score"]} / {postback_dict["num"]}', contents=reply_bubble)]
		if postback_dict['score'] == 0: ## if score is 0, send a sticker
			messages.append(random.choice([
				StickerMessage(packageId="789", stickerId="10887"),
				StickerMessage(packageId="11537", stickerId="52002750"),
				StickerMessage(packageId="11538", stickerId="51626522"),
				StickerMessage(packageId="11539", stickerId="52114149")
			]))
		elif postback_dict['score'] == postback_dict['num']: 
			messages.append(random.choice([
				StickerMessage(packageId="11537", stickerId="52002734"),
				StickerMessage(packageId="11537", stickerId="52002735"),
				StickerMessage(packageId="11538", stickerId="51626505"),
				StickerMessage(packageId="11539", stickerId="52114116")
			]))
		return messages
	
##################################################
	
