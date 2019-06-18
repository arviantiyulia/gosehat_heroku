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

from __future__ import unicode_literals

import datetime as dt
import time as tm
import errno
import os
import sys
import tempfile
from argparse import ArgumentParser

from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (AudioMessage, BeaconEvent, BoxComponent,
                            BubbleContainer, ButtonsTemplate,
                            CameraAction, CameraRollAction, CarouselColumn,
                            CarouselTemplate, ConfirmTemplate,
                            DatetimePickerAction, FileMessage, FlexSendMessage,
                            FollowEvent, ImageCarouselColumn,
                            ImageCarouselTemplate, ImageComponent,
                            ImageMessage, JoinEvent, LeaveEvent,
                            LocationAction, LocationMessage,
                            LocationSendMessage, MessageAction, MessageEvent,
                            PostbackAction, PostbackEvent, QuickReply,
                            QuickReplyButton, SourceGroup,
                            SourceRoom, SourceUser, StickerMessage, StickerSendMessage,
                            TemplateSendMessage, TextComponent, TextMessage,
                            TextSendMessage, UnfollowEvent, URIAction,
                            VideoMessage, ImageSendMessage)

from informasi import get_info
from processing.app import get_cf
from processing.cek_input import cek_total_gejala, cek_total_penyakit
from processing.db import create_connection
from processing.greeting import check_greeting
from processing.preprocessing import (filtering, get_stopword, stemming,
                                      tokenizing)
from processing.save_input import (delete_menukonsultasi, flat, hapus_kata_sakit, save_history,
                                   save_input, save_menuinformasi,
                                   save_menukonsultasi)
from processing.sinonim import get_sinonim
from processing.symptoms import get_symptoms

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', '8b8036d6cf2acdbdb6d4eaf32db728d6')
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN',
                                 'n88a6ebbe8saM6ztF8MF9XSr8APpmCzqQIXDiQMEEGdaEafx2KvewK0Dra7Wbpp/dvHRDKU+nPp0xzaXeO3o68WuTq9p/11qTqd+GKA/8cpH4dgSBLDNnIH9s/v5LYPAtmeBndXjUIBFH2TVnXhuOQdB04t89/1O/w1cDnyilFU=')
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')


# function for create tmp dir for download content
def make_static_tmp_dir():
    try:
        os.makedirs(static_tmp_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(static_tmp_path):
            pass
        else:
            raise


@app.route("/")
def test():
    return 'It Works'


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
    except LineBotApiError as e:
        print("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            print("  %s: %s" % (m.property, m.message))
        print("\n")
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text
    profile = line_bot_api.get_profile(event.source.user_id)

    if text == 'profile':
        if isinstance(event.source, SourceUser):
            # profile = line_bot_api.get_profile(event.source.user_id)
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text='Display name: ' + profile.display_name),
                    TextSendMessage(text='Status message: ' + profile.status_message)
                ]
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Bot can't use profile API without user ID"))
    elif text == 'bye':
        if isinstance(event.source, SourceGroup):
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text='Leaving group'))
            line_bot_api.leave_group(event.source.group_id)
        elif isinstance(event.source, SourceRoom):
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text='Leaving group'))
            line_bot_api.leave_room(event.source.room_id)
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Bot can't leave from 1:1 chat"))
    elif text == 'confirm':
        confirm_template = ConfirmTemplate(text='Do it?', actions=[
            MessageAction(label='Yes', text='Yes!'),
            MessageAction(label='No', text='No!'),
        ])
        template_message = TemplateSendMessage(
            alt_text='Confirm alt text', template=confirm_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif text == 'buttons':
        buttons_template = ButtonsTemplate(
            title='My buttons sample', text='Hello, my buttons', actions=[
                URIAction(label='Go to line.me', uri='https://line.me'),
                PostbackAction(label='ping', data='ping'),
                PostbackAction(label='ping with text', data='ping', text='ping'),
                MessageAction(label='Translate Rice', text='米')
            ])
        template_message = TemplateSendMessage(
            alt_text='Buttons alt text', template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif text == 'carousel':
        carousel_template = CarouselTemplate(columns=[
            CarouselColumn(text='hoge1', title='fuga1', actions=[
                URIAction(label='Go to line.me', uri='https://line.me'),
                PostbackAction(label='ping', data='ping')
            ]),
            CarouselColumn(text='hoge2', title='fuga2', actions=[
                PostbackAction(label='ping with text', data='ping', text='ping'),
                MessageAction(label='Translate Rice', text='米')
            ]),
        ])
        template_message = TemplateSendMessage(
            alt_text='Carousel alt text', template=carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif text == 'image_carousel':
        image_carousel_template = ImageCarouselTemplate(columns=[
            ImageCarouselColumn(text='hoge1', image_url='https://via.placeholder.com/1024x1024',
                                action=DatetimePickerAction(label='datetime',
                                                            data='datetime_postback',
                                                            mode='datetime')),
            ImageCarouselColumn(text='hoge1', image_url='https://via.placeholder.com/1024x1024',
                                action=DatetimePickerAction(label='date',
                                                            data='date_postback',
                                                            mode='date'))
        ])
        template_message = TemplateSendMessage(
            alt_text='ImageCarousel alt text', template=image_carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif text == 'imagemap':
        pass
    elif text == 'image':
        bubble = BubbleContainer(
            direction='ltr',
            hero=ImageComponent(
                url='http://gosehat.heroku.com/static/image/logo_new.png',
                size='full',
                aspect_ratio='20:13',
                aspect_mode='cover',
                # action=URIAction(uri='http://example.com', label='label')
            ),
            body=BoxComponent(
                layout='vertical',
                contents=[
                    # title
                    TextComponent(text='Tentang Aplikasi', weight='bold', size='xl'),
                    # review
                    # BoxComponent(
                    #     layout='baseline',
                    #     margin='md',
                    #     contents=[
                    #         IconComponent(size='sm', url='https://example.com/gold_star.png'),
                    #         IconComponent(size='sm', url='https://example.com/grey_star.png'),
                    #         IconComponent(size='sm', url='https://example.com/gold_star.png'),
                    #         IconComponent(size='sm', url='https://example.com/gold_star.png'),
                    #         IconComponent(size='sm', url='https://example.com/grey_star.png'),
                    #         TextComponent(text='4.0', size='sm', color='#999999', margin='md',
                    #                       flex=0)
                    #     ]
                    # ),
                    # info
                    BoxComponent(
                        layout='vertical',
                        margin='lg',
                        spacing='sm',
                        contents='GoSehat merupakan aplikasi konsultasi kesehatan yang dibangun oleh :'
                                 '1. Arvianti Yulia Maulfa, 2. Entin Martiana Kusumaningtyas, 3. Fadilah Fahrul Hardiansyah '
                                 ''
                        # BoxComponent(
                        #     layout='baseline',
                        #     spacing='sm',
                        #     contents=[
                        #         TextComponent(
                        #             text='GoSehat merupakan aplikasi konsultasi kesehatan yang dibangun oleh :'
                        #                  '1. Arvianti Yulia Maulfa, 2. Entin Martiana Kusumaningtyas, 3. Fadilah Fahrul Hardiansyah '
                        #                  '',
                        #             color='#aaaaaa',
                        #             size='sm',
                        #             # flex=1
                        #         ),
                        #         # TextComponent(
                        #         #     text='Shinjuku, Tokyo',
                        #         #     wrap=True,
                        #         #     color='#666666',
                        #         #     size='sm',
                        #         #     flex=5
                        #         # )
                        #     ],
                        # ),
                        # BoxComponent(
                        #     layout='baseline',
                        #     spacing='sm',
                        #     contents=[
                        #         TextComponent(
                        #             text='Time',
                        #             color='#aaaaaa',
                        #             size='sm',
                        #             flex=1
                        #         ),
                        #         TextComponent(
                        #             text="10:00 - 23:00",
                        #             wrap=True,
                        #             color='#666666',
                        #             size='sm',
                        #             flex=5,
                        #         ),
                        #     ],
                        # ),
                        # ],
                    )
                ],
            ),
            # footer=BoxComponent(
            #     layout='vertical',
            #     spacing='sm',
            #     contents=[
            #         # callAction, separator, websiteAction
            #         SpacerComponent(size='sm'),
            #         # callAction
            #         ButtonComponent(
            #             style='link',
            #             height='sm',
            #             action=URIAction(label='CALL', uri='tel:000000'),
            #         ),
            #         # separator
            #         SeparatorComponent(),
            #         # websiteAction
            #         ButtonComponent(
            #             style='link',
            #             height='sm',
            #             action=URIAction(label='WEBSITE', uri="https://example.com")
            #         )
            #     ]
            # ),
        )
        message = FlexSendMessage(alt_text="hello", contents=bubble)
        line_bot_api.reply_message(
            event.reply_token,
            message
        )
    elif text == 'tentang':
        url = request.url_root + '/static/image/tentang.png'
        app.logger.info("url=" + url)
        text = 'GoSehat merupakan aplikasi konsultasi kesehatan yang dibangun oleh:\n1. Arvianti Yulia Maulfa \n2. Entin ' \
               'Martiana Kusumaningtyas \n3. Fadilah Fahrul Hardiansyah\n'

        line_bot_api.reply_message(
            event.reply_token, [
                ImageSendMessage(url, url),
                TextSendMessage(text=text),
            ]
        )
    elif text == 'quick_reply':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text='Quick reply',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=PostbackAction(label="label1", data="data1")
                        ),
                        QuickReplyButton(
                            action=MessageAction(label="label2", text="text2")
                        ),
                        QuickReplyButton(
                            action=DatetimePickerAction(label="label3",
                                                        data="data3",
                                                        mode="date")
                        ),
                        QuickReplyButton(
                            action=CameraAction(label="label4")
                        ),
                        QuickReplyButton(
                            action=CameraRollAction(label="label5")
                        ),
                        QuickReplyButton(
                            action=LocationAction(label="label6")
                        ),
                    ])))
    else:
        conn = create_connection()
        cursor = conn.cursor()

        # set user_id dan profile (untuk nama)
        user_id = event.source.user_id;
        name_user = line_bot_api.get_profile(event.source.user_id).display_name
        time = dt.datetime.now()

        if dt.datetime.now() < dt.datetime.now().replace(hour=12, minute=0,
                                                         second=0) and dt.datetime.now() > dt.datetime.now().replace(
            hour=0, minute=0, second=0):
            salam = "Selamat Pagi "
        elif dt.datetime.now() > dt.datetime.now().replace(hour=12, minute=0,
                                                           second=0) and dt.datetime.now() < dt.datetime.now().replace(
            hour=18, minute=0, second=0):
            salam = "Selamat Siang "
        elif dt.datetime.now() > dt.datetime.now().replace(hour=18, minute=0, second=0):
            salam = "Selamat Malam "
        else:
            salam = "Assalamualaikum "

        # MENU
        if text == '\informasi':
            messages = "Masukkan informasi yang ingin dicari.\nContoh : 'Apa penyakit maag ?'"
            save_menuinformasi(user_id, name_user, text, conn)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=(messages)))

        elif text == '\konsultasi':
            save_menukonsultasi(user_id, name_user, text, conn)
            messages = "Masukkan keluhan Anda.\nContoh : 'Saya merasa demam, mual pusing muntih. Saya sakit apa ?'"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=(messages)))
        else:
            cursor.execute("SELECT status FROM menu WHERE id_user = '" + user_id + "'")
            count_menu = cursor.fetchall()

        print("DEBUG> count menu = ", count_menu)

        if len(count_menu) != 0:
            if count_menu[0][0] == '\informasi':
                disease_id = 0
                sinonim, penyakit, messages_info = get_info(text)
                if len(penyakit) == 0:
                    messages = check_greeting(sinonim)
                    save_history(user_id, name_user, text, messages, "", disease_id, time, conn)
                else:
                    messages = salam + name_user + "\n" + messages_info[0][0]
                    save_history(user_id, name_user, text, messages_info[0][0], "", disease_id, time, conn)
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=(messages)))
                delete_menukonsultasi(user_id, conn)
            elif count_menu[0][0] == '\konsultasi':
                messages = message_bot(user_id, name_user, salam, text, time, conn)
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=(messages)))
                delete_menukonsultasi(user_id, conn)
        else:
            decision = decide_process(text)
            print("DEBUG> pilihan = ", decision)
            if decision == "informasi":
                disease_id = 0
                sinonim, penyakit, messages_info = get_info(text)
                if len(penyakit) == 0 and len(sinonim) <= 2:
                    # gabung_sinonim = ' '.join(sinonim)
                    messages = check_greeting(sinonim)
                    save_history(user_id, name_user, text, messages, "", disease_id, time, conn)
                else:
                    messages = salam + name_user
                    for msg in messages_info:
                        messages = messages + "\n\n" + msg[0][0]
                    save_history(user_id, name_user, text, messages, "", disease_id, time, conn)
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=(messages)))
            else:
                messages = message_bot(user_id, name_user, salam, text, time, conn)
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=(messages)))
            delete_menukonsultasi(user_id, conn)


def decide_process(text):
    print("\nDEBUG> ------------ DECIDE PROCESS --------------")
    conn = create_connection()
    cursor = conn.cursor()
    stopwords = get_stopword('file/konjungsi_info.csv')
    contents = tokenizing(text)
    filters = filtering(contents, stopwords)
    stems = stemming(filters)
    sinonim = get_sinonim(stems)

    stopword_info_list = ["apa", "kenapa", "mengapa", "bagaimana", "obat", "sebab", "solusi", "gejala", "komplikasi",
                          "cegah"]
    stop_list = [word for word in stopword_info_list if word in sinonim]

    for stop in stop_list:
        sinonim.remove(stop)
    if "sakit" in sinonim:
        sinonim.remove("sakit")
    if "demam" in sinonim:
        sinonim.remove("demam")

    print("DEBUG> sinonim baru = ", sinonim)
    print("DEBUG> stop_list = ", stop_list)

    daftar_gejala, id_gejala, nama_gejala = get_symptoms(conn, sinonim)
    print("DEBUG> daftar gejala", daftar_gejala)

    daftar_penyakit = []
    for i in sinonim:
        cursor.execute("SELECT id_penyakit, nama_penyakit FROM penyakit WHERE nama_penyakit LIKE '%" + i + "%'")
        daftar_penyakit.append(cursor.fetchall())

    daftar_penyakit = [e for e in daftar_penyakit if e]  # list of tuple to list and not empty
    print("DEBUG> daftar penyakit", daftar_penyakit)

    if len(stop_list) != 0:

        print("DEBUG> ------------ END DECIDE PROCESS --------------\n")

        if len(stop_list) >= 1:
            if len(daftar_penyakit) == 0 and len(daftar_gejala) < 2:
                return "informasi"
            elif len(daftar_penyakit) > 0 and len(daftar_gejala) < 2:
                return "informasi"
            else:
                return "konsultasi"

        else:
            return "informasi"

    else:
        if len(sinonim) == 1 and "tidak" in sinonim:
            return "konsultasi"
        if len(daftar_penyakit) == 0 and len(daftar_gejala) < 2:
            return "informasi"
        elif len(daftar_penyakit) > 0 and len(daftar_gejala) < 2:
            return "informasi"
        else:
            return "konsultasi"


def message_bot(user_id, name_user, salam, text, time, conn):
    msg_penyakit = "Kemungkinan Anda terkena penyakit "
    msg_pengobatan = "\n\n#Pengobatan \nPertolongan pertama yang bisa dilakukan adalah "
    msg_pencegahan = "\n#Pencegahan \nPencegahan yang bisa dilakukan adalah "
    msg_peringatan = "Silahkan menghubungi dokter untuk mendapatkan informasi dan penanganan yang lebih baik"

    message = ""
    timestamp = tm.time()
    penyakit_result = ""
    definisi_result = ""
    disease = ""

    cursor = conn.cursor()

    if text.lower() == 'tidak':
        kondisi_gejala = 'ada'
        sinonim = []
    else:
        stopwords = get_stopword('file/konjungsi.csv')
        contents = tokenizing(text)
        filters = filtering(contents, stopwords)
        stems = stemming(filters)
        sinonim = get_sinonim(stems)
        hapus_kata_sakit(sinonim)

        if len(sinonim) <= 2 :
            gabung_sinonim = ' '.join(sinonim)

            if gabung_sinonim == 'selamat pagi' or gabung_sinonim == 'selamat malam' or gabung_sinonim == 'pagi' or gabung_sinonim == 'malam':
                greeting = check_greeting(sinonim)
                disease_id = 0
                save_history(user_id, name_user, text, greeting, "", disease_id, time, conn)
                return greeting

        symp_db, symptoms, input = get_symptoms(conn, sinonim)
        kondisi_gejala = cek_total_gejala(symp_db)
        jml_penyakit, penyakit = cek_total_penyakit(conn, sinonim)

        cursor.execute("SELECT DISTINCT input_user, time FROM gejala_input WHERE user_id = '" + user_id + "'")
        get_time = cursor.fetchall()

        print("get time = ", get_time)
        if get_time:
            timestamp_now = tm.time() - float(get_time[0][1])

            if timestamp_now >= 3600:
                cursor.execute("DELETE FROM gejala_input WHERE user_id = '" + user_id + "'")
                conn.commit()
                print("hapus gejala expired")


    # jika gejala kosong maka tampilkan pesan
    if kondisi_gejala == "kosong":
        print("INFO> gejala kosong")
        disease_id = 0
        print("DEBUG> jumlah penyakit = ", jml_penyakit)
        if jml_penyakit == 0:
            disease = check_greeting(sinonim)
        elif jml_penyakit > 0:
            for pnykt in penyakit:
                disease = disease + pnykt[0][2] + "\n\n"

        message = message + str(disease)
        save_history(user_id, name_user, text, message, "", disease_id, time, conn)

    # jika gejalanya kurang
    elif kondisi_gejala == "kurang":
        print("INFO> gejala kurang")

        input_to_sinonim = ",".join(input)
        print("DEBUG> Sinonim disimpan ke tabel (gejala input) = ", input_to_sinonim)
        save_input(user_id, name_user, symp_db, input_to_sinonim, timestamp, conn)

        cursor.execute("SELECT COUNT (*) FROM gejala_input WHERE user_id = '" + user_id + "'")
        count_input = cursor.fetchall()

        if count_input[0][0] <= 3:
            message = message + "Apakah ada gejala lain ?\n\nGejala yang anda masukkan kurang. Masukkan minimal 4 gejala agar mendapatkan hasil yang akurat. \n\n Atau jawab TIDAK jika tidak ada gejala yang ingin ditambahkan."
            disease_id = 0
            save_history(user_id, name_user, input_to_sinonim, message, "", disease_id, time, conn)


        else:
            cursor.execute("SELECT nama_gejala FROM gejala_input WHERE user_id = '" + user_id + "'")
            gejala_db = cursor.fetchall()
            print("DEBUG> Kurang | Gejala di DB = ", gejala_db)
            gejala = [i[0].split(',') for i in gejala_db]
            gejala_flat = flat(gejala)
            print("DEBUG> Kurang | Gejala yang digabung = ", gejala_flat)
            result, cf = get_cf(conn, gejala_flat)

            # jika yang terdeteksi hanya 1 penyakit
            if len(result) == 1:
                for output in result:
                    message = message + salam + name_user + "\n" \
                              + msg_penyakit + output[0][1] + "\n" + output[0][2] \
                              + msg_pengobatan + output[0][4] + "\n" \
                              + msg_pencegahan + output[0][5] + "\n\n" \
                              + (str(output[0][6]) + "\n\n" if output[0][6] is not None else '') \
                              + msg_peringatan

                output_sistem = msg_penyakit + result[0][0][1]
                disease_id = result[0][0][0]
                save_history(user_id, name_user, text, output_sistem, "", disease_id, time, conn)


            # jika yang terdeteksi lebih dari 1 penyakit
            else:
                for idx in result:
                    penyakit_result = penyakit_result + " , " + idx[0][1]
                    definisi_result = definisi_result + "\n\n" + idx[0][2]

                message = message + salam + name_user + "\n" + msg_penyakit + penyakit_result + "\n" + definisi_result + "\n\n" + msg_peringatan
                output_sistem = msg_penyakit + penyakit_result

                for dis in result:
                    disease_id = dis[0][0]
                    save_history(user_id, name_user, text, output_sistem, "", disease_id, time, conn)

            cursor.execute("DELETE FROM gejala_input WHERE user_id = '" + user_id + "'")
            conn.commit()

    # setelah sukses hapus yang ada di db
    elif kondisi_gejala == "ada":
        print("INFO> gejala cukup")
        cursor.execute("SELECT DISTINCT input_user, time FROM gejala_input WHERE user_id = '" + user_id + "'")
        gejala_db = cursor.fetchall()

        print("DEBUG> Cukup | Gejala di DB = ", gejala_db)

        if not gejala_db:
            if len(sinonim) == 0:
                disease = check_greeting(sinonim)
                message = message + str(disease)
                return message
            else:
                result, cf = get_cf(conn, sinonim)
                # untuk mendapatkan daftar string gejala
                print("\n----------proses dibawah ini untuk daftar gejala yang disimpan ke histroy------------")
                symp_db, symptoms, input = get_symptoms(conn, sinonim)
                string_gejala = ', '.join([symp[0][1] for symp in symp_db])
                print("-------------------------selesai-------------------------\n")

        else:
            gejala = [i[0].split(',') for i in gejala_db]
            gejala_flat = flat(gejala)
            print("DEBUG> Cukup | Gejala yang digabung = ", gejala_flat)
            gejala_new2 = sinonim + gejala_flat
            print("DEBUG> Cukup | Gejala yang digabung + kalimat sebelum = ", gejala_new2)

            # untuk mendapatkan daftar string gejala
            print("\n----------proses dibawah ini untuk daftar gejala yang disimpan ke histroy------------")
            symp_db, symptoms, input = get_symptoms(conn, gejala_new2)
            string_gejala = ', '.join([symp[0][1] for symp in symp_db])
            print("-------------------------selesai-------------------------\n")

            if len(symp_db) <= 1:
                disease_id = 0
                output_sistem = "Maaf data kurang akurat. Sistem tidak bisa memberikan diagnosa.\nSilahkan masukkan keluhan Anda kembali."
                save_history(user_id, name_user, text, output_sistem, string_gejala, disease_id, time, conn)
                cursor.execute("DELETE FROM gejala_input WHERE user_id = '" + user_id + "'")
                conn.commit()
                return salam + name_user + "\n" + output_sistem
            else:
                result, cf = get_cf(conn, gejala_new2)

            cursor.execute("DELETE FROM gejala_input WHERE user_id = '" + user_id + "'")
            conn.commit()

        # jika yang terdeteksi hanya 1 penyakit
        if len(result) == 1:
            for output in result:
                message = message + salam + name_user + "\n" \
                          + msg_penyakit + output[0][1] + "\n" + output[0][2] \
                          + msg_pengobatan + output[0][4] + "\n" \
                          + msg_pencegahan + output[0][5] + "\n\n" \
                          + (str(output[0][6]) + "\n\n" if output[0][6] is not None else '') \
                          + msg_peringatan

            output_sistem = msg_penyakit + result[0][0][1]
            disease_id = result[0][0][0]
            save_history(user_id, name_user, text, output_sistem, string_gejala, disease_id, time, conn)

        # jika yang terdeteksi lebih dari 1 penyakit
        else:
            for idx in result:
                print("DEBUG> Penyakit lebih > 1 | Penyakit = ", idx)
                penyakit_result = penyakit_result + " , " + idx[0][1]
                definisi_result = definisi_result + "\n\n" + idx[0][2]

            message = message + salam + name_user + "\n" + msg_penyakit + penyakit_result + "\n" + definisi_result + "\n\n" + msg_peringatan
            output_sistem = msg_penyakit + penyakit_result

            for dis in result:
                disease_id = dis[0][0]
                save_history(user_id, name_user, text, output_sistem, string_gejala, disease_id, time, conn)

    return message


@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        LocationSendMessage(
            title=event.message.title, address=event.message.address,
            latitude=event.message.latitude, longitude=event.message.longitude
        )
    )


@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        StickerSendMessage(
            package_id=event.message.package_id,
            sticker_id=event.message.sticker_id)
    )


# Other Message Type
@handler.add(MessageEvent, message=(ImageMessage, VideoMessage, AudioMessage))
def handle_content_message(event):
    if isinstance(event.message, ImageMessage):
        ext = 'jpg'
    elif isinstance(event.message, VideoMessage):
        ext = 'mp4'
    elif isinstance(event.message, AudioMessage):
        ext = 'm4a'
    else:
        return

    message_content = line_bot_api.get_message_content(event.message.id)
    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix=ext + '-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        tempfile_path = tf.name

    dist_path = tempfile_path + '.' + ext
    dist_name = os.path.basename(dist_path)
    os.rename(tempfile_path, dist_path)

    line_bot_api.reply_message(
        event.reply_token, [
            TextSendMessage(text='Save content.'),
            TextSendMessage(text=request.host_url + os.path.join('static', 'tmp', dist_name))
        ])


@handler.add(MessageEvent, message=FileMessage)
def handle_file_message(event):
    message_content = line_bot_api.get_message_content(event.message.id)
    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix='file-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        tempfile_path = tf.name

    dist_path = tempfile_path + '-' + event.message.file_name
    dist_name = os.path.basename(dist_path)
    os.rename(tempfile_path, dist_path)

    line_bot_api.reply_message(
        event.reply_token, [
            TextSendMessage(text='Save file.'),
            TextSendMessage(text=request.host_url + os.path.join('static', 'tmp', dist_name))
        ])


@handler.add(FollowEvent)
def handle_follow(event):
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(
            text='SELAMAT DATANG DI GOSEHAT! \n\nGoSehat adalah chatbot (aplikasi pintar) yang dapat digunakan untuk '
                 'konsultasi kesehatan secara gratis! Anda dapat bertanya seputar kesehatan seperti pengobatan, '
                 'pencegahan, atau penyebab suatu penyakit. \n\nCukup kirim pesan apa yang ingin Anda tanyakan atau '
                 'memilih menu yang tersedia ya.\ncontoh: "Saya sering mengalami pusing, mual, batuk. Saya '
                 'sakit apa ?" atau menanyakan informasi seperti "Haloo, untuk obat maag apa ya?" \n\nTahapan pemakaian '
                 'aplikasi GoSehat :\n1. Ketikkan pesan seperti pada contoh diatas atau pilih menu \n2. Anda bisa '
                 'mengetikkan gejala untuk mendeteksi penyakit pada tubuh Anda\n3. Anda bisa mengetikkan nama penyakit '
                 'untuk mengetahui jenis penyakit\n4. Tunggu hingga aplikasi memberikan Anda jawaban\n\nTetap jaga '
                 'kesehatan ya!'))


@handler.add(UnfollowEvent)
def handle_unfollow():
    app.logger.info("Got Unfollow event")


@handler.add(JoinEvent)
def handle_join(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='Joined this ' + event.source.type))


@handler.add(LeaveEvent)
def handle_leave():
    app.logger.info("Got leave event")


@handler.add(PostbackEvent)
def handle_postback(event):
    if event.postback.data == 'ping':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='pong'))
    elif event.postback.data == 'datetime_postback':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.postback.params['datetime']))
    elif event.postback.data == 'date_postback':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.postback.params['date']))


@handler.add(BeaconEvent)
def handle_beacon(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(
            text='Got beacon event. hwid={}, device_message(hex string)={}'.format(
                event.beacon.hwid, event.beacon.dm)))


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', type=int, default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    # create tmp dir for download content
    make_static_tmp_dir()

    app.run(debug=options.debug, port=options.port)
