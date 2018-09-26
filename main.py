# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

import os
import sys
from argparse import ArgumentParser

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
)
from janome.tokenizer import Tokenizer
from wordcloud import WordCloud
import matplotlib

app = Flask(__name__)
 
# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

"""
@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text)
    )
"""

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
	text = event.message.text
	t = Tokenizer()
	output = []
	for token in t.tokenize(text):
		if token.part_of_speech.split(',')[0] == "動詞":
			output.append(token.surface)
		elif token.part_of_speech.split(',')[0] == "形容詞":
			output.append(token.surface)
		elif token.part_of_speech.split(',')[0] == "副詞":
			output.append(token.surface)
		elif token.part_of_speech.split(',')[0] == "名詞":
			output.append(token.surface)
	a = ""

	stop_words = [ u'てる', u'いる', u'なる', u'れる', u'する', u'ある', u'こと', u'これ', u'さん', u'して', \
				 u'くれる', u'やる', u'くださる', u'そう', u'せる', u'した',  u'思う',  \
				 u'それ', u'ここ', u'ちゃん', u'くん', u'', u'て',u'に',u'を',u'は',u'の', u'が', u'と', u'た', u'し', u'で', \
				 u'ない', u'も', u'な', u'い', u'か', u'ので', u'よう', u'ます', u'まし', u'から', 'です', u'だっ', u'だい', u'あり', u'たい', u'って', u'ほど', u'とか', u'なり']

	for word in output:
		word = "\t" + str(word)
		a = a + str(word) 

	wordcloud = WordCloud(background_color="white", font_path = "FgFumi.ttf", width=800, height=600, stopwords=set(stop_words))
	wordcloud.generate(a)
	wordcloud.to_file("wordcloud.png")
	
	line_bot_api.reply_message(
		event.reply_token,[
			ImageSendMessage(
				original_content_url="wordcloud.png", 
				preview_image_url="wordcloud.png"
			)
		]
	)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)