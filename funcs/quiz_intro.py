
from funcs.utils import *
import random, urllib

from linebot.v3.messaging import (
	TextMessage, QuickReply, QuickReplyItem, StickerMessage, AudioMessage,
	PostbackAction, FlexMessage, FlexBubble, FlexBox, FlexText
)

##################################################

## function to get answer and other choices
def create_intro_quiz(previous_answer_ids=[], level=1, num_choices=4):
	## exclude previous answer, and sample
	selected_song = INTRO_QUIZ[INTRO_QUIZ.level <= level].drop(index=previous_answer_ids).sample(num_choices)
	answer_id = selected_song.index[0]  ## ID of correct answer -> use next question to exclude
	answer_title = selected_song['song'].values[0]  ## title of correct answer
	wrong_titles = selected_song['song'].values[1:]  ## title of wrong answers 
	duration = selected_song['duration'].values[0]  ## duration of answer (it must be specified in AudioMessage)
	answer_song_url = f"https://github.com/nozomiyamada/linebot/raw/main/data/intro/{urllib.parse.quote(answer_title)}.mp3"
	
	return answer_id, answer_title, wrong_titles, duration, answer_song_url

def create_introquiz_postback(postback):

	postback_dict = parse_postback(postback) ## convert str to dict
	level = postback_dict['level']

	## ÎF LV IS NOT SPECIFIED - START INTRO QUIZ AND SELECT LEVEL
	if level == 0:
		quickreply = QuickReply(items=[])  ## instantiation
		for l in range(1, 5):
			label = {1:'beginner', 2:'normal', 3:'hard', 4:'all songs'}[l]
			postback_dict['level'] = l
			if l == 4:
				postback_dict['num_q'] = 10  ## 10 question for god level
			item = QuickReplyItem(action=PostbackAction(label=label, displayText=label, data=encode_postback(postback_dict)))
			quickreply.items.append(item)
		return [TextMessage(text='select level', quickReply=quickreply)]
	
	answer = postback_dict['answer']  ## previous answer
	postback_dict['question'] += 1 ## present question number + 1
	reply_bubble = FlexBubble()

	## HEADER - display previous answer
	if answer == 'NONE': ## first question
		reply_bubble.header =FlexBox(
			layout='vertical',
			contents = [FlexText(text='Intro Quiz Start!')]
		)
	else: 
		answer_text = FlexText(text=f'Answer : {answer}', wrap=True) ## the answer of previous question
		if postback_dict['correct'] == 'T':
			correct_or_not = FlexText(text='Correct!', weight='bold', color='#55BB36') ## green
		else:
			correct_or_not = FlexText(text='Wrong!', weight='bold', color='#CB444A') ## red
		reply_bubble.header = FlexBox(
			layout = 'vertical',
			contents = [answer_text, correct_or_not] 
		)

	## MAKE QUICK REPLY ITEMS
	if postback_dict['question'] <= postback_dict['num_q']: ## present question No. <= total num
		num_choices = {1:4, 2:4, 3:5, 4:6}[level]
		
		answer_id, answer_title, wrong_titles, duration, answer_song_url = create_intro_quiz(postback_dict['asked'], level, num_choices) ## drop previous answer
		
		postback_dict['answer'] = answer_title  ## update answer song
		postback_dict['asked'].append(answer_id)  ## update asked questions
		
		quickreply_buttons = []  ## assign to message object
		
		## ADD WRONG ANSWER BUTTON
		postback_dict['correct'] = 'F'
		for title in wrong_titles:
			label = get_label(title)  ## trim label within 20 chrs
			item = QuickReplyItem(action=PostbackAction(label=label, displayText=title, data=encode_postback(postback_dict)))
			quickreply_buttons.append(item)

		## ADD CORRECT ANSWER BUTTON
		postback_dict['score'] += 1  ## add score only correct answer
		postback_dict['correct'] = 'T'
		label = get_label(answer_title)
		item = QuickReplyItem(action=PostbackAction(label=label, displayText=answer_title, data=encode_postback(postback_dict)))
		quickreply_buttons.append(item)

		## SHUFFLE ORDER
		quickreply = QuickReply(items=random.sample(quickreply_buttons, num_choices))

		## FOOOTER - DISPLAY QUESTION No.
		reply_bubble.footer = FlexBox(
			layout='vertical',
			backgroundColor='#EEEEEE',
			paddingAll='xs',
			contents=[FlexText(text=f'QUESTION {postback_dict["question"]} :', size='lg', weight='bold', align='center')]
		)

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
			contents=[FlexText(text=f'SCORE : {postback_dict["score"]} / {postback_dict["num_q"]}', size='xl', weight='bold', align='center')]
		)

		## FOOTER - evaluation message
		if postback_dict['num_q'] == 5:
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
		messages = [FlexMessage(altText=f'SCORE : {postback_dict["score"]} / {postback_dict["num_q"]}', contents=reply_bubble)]
		if postback_dict['score'] == 0: ## if score is 0, send a sticker
			messages.append(random.choice([
				StickerMessage(packageId="789", stickerId="10887"),
				StickerMessage(packageId="11537", stickerId="52002750"),
				StickerMessage(packageId="11538", stickerId="51626522"),
				StickerMessage(packageId="11539", stickerId="52114149")
			]))
		elif postback_dict['score'] == postback_dict['num_q']: 
			messages.append(random.choice([
				StickerMessage(packageId="11537", stickerId="52002734"),
				StickerMessage(packageId="11537", stickerId="52002735"),
				StickerMessage(packageId="11538", stickerId="51626505"),
				StickerMessage(packageId="11539", stickerId="52114116")
			]))
		return messages
	
##################################################
	
