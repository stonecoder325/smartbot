# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

import os
import sys
import random
import requests
from opencc import OpenCC

from wsgiref.simple_server import make_server
from argparse import ArgumentParser

from builtins import bytes
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, StickerMessage, TextSendMessage, ImageSendMessage, StickerSendMessage,
    TemplateSendMessage, ButtonsTemplate, MessageTemplateAction, URITemplateAction, PostbackTemplateAction,
    CarouselTemplate, CarouselColumn
)
from linebot.utils import PY3

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)
# channel_secret = 'ff575ec3465dd7962f5e29ba830dec47'
# channel_access_token = 'SzkNL+H1Q1+eAV5iy3rUyueP8IgMA1cxjBe3NlDtlJCY0HJXNKYoZPZ3idB3JGIYbYmv7pQiNTNtfbKxshhUMWy5/w8a9kDWpmI6Z+3wm8IZ9Vcb/xoelnCCvSB8thfp8YhlotZOyFDhmfgWiGBN0gdB04t89/1O/w1cDnyilFU='
line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


def application(environ, start_response):
    # check request path
    print('application: ', environ['PATH_INFO'])
    if environ['PATH_INFO'] != '/callback':
        start_response('404 Not Found', [])
        return create_body('Not Found')

    # check request method
    if environ['REQUEST_METHOD'] != 'POST':
        start_response('405 Method Not Allowed', [])
        return create_body('Method Not Allowed')

    # get X-Line-Signature header value
    signature = environ['HTTP_X_LINE_SIGNATURE']

    # get request body as text
    wsgi_input = environ['wsgi.input']
    content_length = int(environ['CONTENT_LENGTH'])
    body = wsgi_input.read(content_length).decode('utf-8')

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        start_response('400 Bad Request', [])
        return create_body('Bad Request')

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        print('event: ', event)
        print('event.type: ', event.type)
        print('event.message: ', event.message)

        if not isinstance(event, MessageEvent):
            continue
        if isinstance(event.message, TextMessage):
            m_text = event.message.text.lower()
            if m_text == 'hi':
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text='你好')
                )
            elif m_text == '好看的':
                image_url = 'https://i.imgur.com/OqESt0b.jpeg'
                line_bot_api.reply_message(
                    event.reply_token,
                    ImageSendMessage(original_content_url=image_url, preview_image_url=image_url)
                )
            elif m_text == '天氣':
                r = requests.get('https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=CWB-E24E5D1A-087F-429E-A376-E2E1D25A0F60&locationName=%E6%96%B0%E5%8C%97%E5%B8%82&elementName=MaxT')
                r.encoding = 'utf-8'
                cc = OpenCC('s2tw')
                locate = cc.convert(r.json()['records']['location'][0]['locationName'])
                temp = cc.convert(r.json()['records']['location'][0]['weatherElement'][0]['time'][0]['parameter']['parameterName'])
                res = locate + '的氣溫為'+temp+'C'
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=res)
                )
            elif m_text == 't1':
                image_url = 'https://i.imgur.com/OqESt0b.jpeg'
                buttons_template = TemplateSendMessage(
                    alt_text='Buttons Template',
                    template=ButtonsTemplate(
                        title='ButtonsTemplate',
                        text='Buttons title',
                        thumbnail_image_url=image_url,
                        actions=[
                            MessageTemplateAction(
                                label='問天氣',
                                text='天氣'
                            ),
                            URITemplateAction(
                                label='看大圖',
                                uri=image_url
                            )
                            # PostbackTemplateAction(
                            #     label='Postback',
                            #     text='Postback',
                            #     data='action=buy&itemid=0'
                            # )
                        ]
                    )
                )
                line_bot_api.reply_message(event.reply_token, buttons_template)
            elif m_text == 't2':
                buttons_template = TemplateSendMessage(
                    alt_text='Carousel template',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                title='Carousel template 1',
                                text='Carousel template 1',
                                thumbnail_image_url='https://www.ttshow.tw/media/uploads/2020/02/07/1561674586.JPG',
                                actions=[
                                    MessageTemplateAction(
                                        label='Message1',
                                        text='Message1'
                                    ),
                                    URITemplateAction(
                                        label='URI1',
                                        uri='https://www.ttshow.tw/media/uploads/2020/02/07/1561674586.JPG'
                                    )
                                    # PostbackTemplateAction(
                                    #     label='Postback1',
                                    #     text='Postback1',
                                    #     data='action=buy&itemid=1'
                                    # )
                                ]
                            ),
                            CarouselColumn(
                                title='Carousel template 2',
                                text='Carousel template 2',
                                thumbnail_image_url='https://www.mrplayer.tw/photos/shares/1709272/fun_201709274/59cb3f9a95f72.png',
                                actions=[
                                    MessageTemplateAction(
                                        label='Message2',
                                        text='Message1'
                                    ),
                                    URITemplateAction(
                                        label='URI2',
                                        uri='https://www.mrplayer.tw/photos/shares/1709272/fun_201709274/59cb3f9a95f72.png'
                                    )
                                    # PostbackTemplateAction(
                                    #     label='Postback2',
                                    #     text='Postback2',
                                    #     data='action=buy&itemid=2'
                                    # )
                                ]
                            )
                        ]
                    )
                )
                line_bot_api.reply_message(event.reply_token, buttons_template)
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=event.message.text)
                )
        if isinstance(event.message, StickerMessage):
            line_bot_api.reply_message(
                event.reply_token,
                StickerSendMessage(package_id=3, sticker_id=random.randint(180, 220))
            )
        else:
            continue
    start_response('200 OK', [])
    return create_body('OK')


def create_body(text):
    if PY3:
        return [bytes(text, 'utf-8')]
    else:
        return text


if __name__ == '__main__':
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    # arg_parser.add_argument('-p', '--port', type=int, default=5000, help='port')
    # options = arg_parser.parse_args()
    port = int(os.getenv('PORT', default=8000))
    httpd = make_server('0.0.0.0', port, application)
    print('port ', port)
    httpd.serve_forever()
