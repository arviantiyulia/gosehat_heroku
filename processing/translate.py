# import os
# from google_api_translate import Translator, TextUtils
# creds_path = os.path.join(os.path.dirname(__file__), '../file/Tugas Akhir.json')
#
# html_str = 'karna'
# s = Translator(creds_path=creds_path).html(text=html_str, target_language='in')
# print(s.text)

from googletrans import Translator

text = "knapa"
translator = Translator()
trans = translator.translate(text, src='id', dest='en')
trans = translator.translate(trans.text, src='en', dest='id')
print(trans.text)