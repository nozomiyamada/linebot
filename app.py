# -*- coding: utf-8 -*-
from flask import Flask, request, abort, render_template
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
	ApiClient, Configuration, MessagingApi,
	ReplyMessageRequest, TextMessage
)
from linebot.v3.webhooks import (
	FollowEvent, MessageEvent, PostbackEvent, TextMessageContent
)
from google import genai
from google.genai import types
import os, re, random

from funcs import *

## load `.env` file
## if test bot, use `load_dotenv('test.env', override=True)` instead 
from dotenv import load_dotenv
load_dotenv()

## environment variables
CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
CHANNEL_SECRET = os.environ["CHANNEL_SECRET"]
GEMINI_APIKEY = os.environ['GEMINI_APIKEY']

## Flask instantiation
app = Flask(__name__)

## LINE instantiation
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

## GEMINI instantiation
gemini_client = genai.Client(api_key=GEMINI_APIKEY)
instruction = """あなたは日本語とタイ語の先生です。
日本語からタイ語翻訳の場合はカタカナでなく発音記号をつけてください。
その際に表記は The Royal Thai General System of Transcription に従い、国際音声記号ではなく声調記号付きアルファベットで出力してください。
その際に大文字にする必要はありません。

以下は回答例です。

質問：
あなたは明日どこへ行って何を食べますか？

回答：
พรุ่งนี้คุณจะไปที่ไหนและทานอะไร
[phrûngníi khun cà pai thîinǎi láe thaan arai]

- พรุ่งนี้ (phrûngníi): 明日
- คุณ (khun): あなた
- จะ (cà): ～するつもり
- ไป (pai): 行く
- ที่ไหน (thîinǎi): どこ
- และ (láe): そして
- ทาน (thaan): 会う
- อะไร (arai): 何"""

## callback function (copied from official GitHub)
@app.route("/callback", methods=['POST'])
def callback():
	signature = request.headers['X-Line-Signature']
	body = request.get_data(as_text=True)
	app.logger.info("Request body: " + body)
	try:
		handler.handle(body, signature)
	except InvalidSignatureError:
		app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
		abort(400)
	return 'OK'

##################################################

## When someone follows the bot
@handler.add(FollowEvent)
def handle_follow(event):
	## API instantiation
	with ApiClient(configuration) as api_client:
		line_bot_api = MessagingApi(api_client)
	## send reply message
	line_bot_api.reply_message(ReplyMessageRequest(
		replyToken=event.reply_token,
		messages=[TextMessage(text='Thank You for adding me!')] + create_flex_howtouse()
	))

## When received TEXT MESSAGE
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
	with ApiClient(configuration) as api_client:
		line_bot_api = MessagingApi(api_client)
	## get the text content
	received_message = event.message.text.strip().lower() ## remove spaces

	if 'how to use' in received_message:
		messages = create_flex_howtouse()
	## MODE : LYRICS
	elif re.match(r'(歌詞|lyrics?)', received_message):
		query = re.sub(r'^(歌詞|lyrics?)', '', received_message)  ## remove prefix
		messages = get_lyrics(query)
	## MODE : HARMONY
	elif re.match(r'(harmony|chorus|コーラス)', received_message):
		query = re.sub(r'^(harmony|chorus|コーラス)', '', received_message)  ## remove prefix
		messages = get_harmony(query)
	## MODE : BASSTAB
	elif re.match(r'(bass\s?tab|ベースタブ|ベースtab)', received_message):
		query = re.sub(r'^(bass\s?tab|ベースタブ|ベースtab)', '', received_message)  ## remove prefix
		messages = get_basstab(query)
	## MODE : BASS
	elif re.match(r'(bass|ベース)', received_message):
		query = re.sub(r'^(bass|ベース)', '', received_message)  ## remove prefix
		messages = get_bass(query)
	## MODE : INFO
	elif re.match(r'(info|データ)', received_message):
		query = re.sub(r'^(info|データ)', '', received_message)  ## remove prefix
		messages = get_info(query)
	## MODE : RANDOM
	elif re.match(r'(random|ランダム)', received_message):
		messages = get_official_youtube(random.choice(SONGS))
	## MODE : LYRICS QUIZ
	elif re.match(r'(歌詞\s*)?(クイズ|quiz)', received_message):
		postback = 'mode=lyricsquiz&level=0&num_q=5&question=0&score=0&answer=NONE&asked=@&correct=T'
		messages = create_lyricsquiz_postback(postback=postback)
	## MODE : LYRICS QUIZ
	elif re.match(r'(intro|イントロ)(quiz|クイズ)?', received_message):
		postback = 'mode=introquiz&level=0&num_q=5&question=0&score=0&answer=NONE&asked=@&correct=T'
		messages = create_introquiz_postback(postback=postback)
	## MODE : THAI TRANSLATION
	elif re.match(r'(タイ語?|翻訳)', received_message):
		content = re.replace(r'(タイ語?|翻訳)', '', received_message).strip()
		response = gemini_client.models.generate_content(
			model='gemini-2.0-flash-001',
			contents=content,
			config=types.GenerateContentConfig(system_instruction=instruction),
		)
		messages = response.text
	## MODE : OFFICIAL YOUTUBE
	else:
		messages = get_official_youtube(received_message)

	## send reply message
	line_bot_api.reply_message(ReplyMessageRequest(
		replyToken=event.reply_token,
		messages=messages
	))

## When received POSTBACK EVENT - lyrics quiz
@handler.add(PostbackEvent)
def handle_postback(event):
	with ApiClient(configuration) as api_client:
		line_bot_api = MessagingApi(api_client)
	
	## get the postback data
	postback_data = event.postback.data

	## get replay message - QuickReply(with postback) or TextMessage
	if 'mode=lyricsquiz' in postback_data:
		messages = create_lyricsquiz_postback(postback=postback_data)
	elif 'mode=introquiz' in postback_data:
		messages = create_introquiz_postback(postback=postback_data)

	## send reply message
	line_bot_api.reply_message(ReplyMessageRequest(
		replyToken=event.reply_token,
		messages=messages
	))

##################################################

## LIFF APP
@app.route('/', methods=['GET'])
def liffpage():
	return render_template('index.html')

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=8000, debug=True)