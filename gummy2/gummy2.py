import os
import sqlite3
from flask import Flask, request, g, redirect, url_for, abort, render_template, flash, jsonify
from flask_bootstrap import Bootstrap
from translate import Translator
import urllib
import speech_recognition as sr
import soundfile as sf
import subprocess as sp
from gtts import gTTS

app = Flask(__name__)
Bootstrap(app)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'gummy2.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))

def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

@app.route('/')
def home():
    remove_files()
    return render_template('home.html')

@app.route('/_check_locale', methods=['GET'])
def check_locale():
    language_name = request.args.get('language_name', '', type=str)
    language_locale = request.args.get('language_locale', '', type=str)

    translate = Translator(from_lang='en-US', to_lang=language_locale)

    translated_text = translate.translate('test')

    if 'INVALID TARGET LANGUAGE' in translated_text:
        return jsonify('invalid')
    else:
        try:
            tts = gTTS(text='test', lang=language_locale)
            return jsonify('valid')
        except Exception:
            return jsonify('not supported')

@app.route('/_translate', methods=['GET'])
def translate():
    remove_files()

    text = request.args.get('text', '', type=unicode)
    lang_to = request.args.get('lang_to', '', type=str)
    lang_from = request.args.get('lang_from', '', type=str)

    print request.args
    
    translate = Translator(to_lang=lang_to, from_lang=lang_from)

    try:
        translated_text = translate.translate(text)
    except KeyError:
        try:
            translated_text = translate.translate(str(text))
        except UnicodeEncodeError:
            translated_text = urllib.quote(translate.translate(text.encode('utf-8')))
    except UnicodeEncodeError:
        translated_text = urllib.quote(translate.translate(text.encode('utf-8')))

    save_speech_mp3_files(text, translated_text, lang_from, lang_to)
    return jsonify(urllib.unquote(translated_text))

@app.route('/_record_voice', methods=['POST'])
def record_voice():
    remove_files()
    try:
        lang = request.form.get('language')

        f = open('speech.ogg', 'wb')
        f.write(request.files['file'].read())
        f.close()

        cmdline = [
            'avconv',
            '-i',
            'speech.ogg',
            '-vn',
            '-f',
            'wav',
            'speech.wav'
        ]

        sp.call(cmdline)

        r = sr.Recognizer()
        with sr.AudioFile('speech.wav') as source:
            audio = r.record(source)
    
        text = r.recognize_google(audio, language=str(lang))
    except Exception:
        text = 'Unable to understand'
    finally:
        print 'language: ' + lang
        print 'text: ' + text
        return jsonify(text)

def save_speech_mp3_files(text, translated_text, text_lang, translated_text_lang):
    UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__))
    print UPLOAD_FOLDER

    tts_en = gTTS(text=text.encode('utf-8'), lang=text_lang)
    tts_en.save(os.path.join(UPLOAD_FOLDER, 'static', 'speech_left.mp3'))
    tts_ja = gTTS(text=translated_text.encode('utf-8'), lang=translated_text_lang)
    tts_ja.save(os.path.join(UPLOAD_FOLDER, 'static', 'speech_right.mp3'))

def remove_files():
    array_files = ['speech.ogg', 'speech.wav', 'en_speech.mp3', 'ja_speech.mp3']
    for f in array_files:
        if os.path.exists(f):
            os.remove(f)
