import os
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

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/_ja_translate', methods=['GET'])
def ja_translate():
    remove_files()
    text = request.args.get('text', '', type=str)

    translate = Translator(to_lang='ja', from_lang='en-US')
    translated_text = translate.translate(text)

    save_speech_mp3_files(text, translated_text)
    return jsonify(translated_text)

@app.route('/_en_translate', methods=['GET'])
def en_translate():
    remove_files()
    text = request.args.get('text', '', type=unicode)

    translate = Translator(to_lang='en-US', from_lang='ja')
    translated_text = urllib.quote(translate.translate(text.encode('utf-8')))

    save_speech_mp3_files(urllib.unquote(translated_text), text)
    return jsonify(translated_text)

@app.route('/_translate_en_record', methods=['POST'])
def translate_en_record():
    remove_files()

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
    
    try:
        text = r.recognize_google(audio)
    except Exception:
        text = 'Unable to understand'
    finally:
        print 'text: ' + text
        return jsonify(text)

def save_speech_mp3_files(en_text, ja_text):
    tts_en = gTTS(text=en_text, lang='en')
    tts_en.save('en_speech.mp3')
    tts_ja = gTTS(text=ja_text.encode('utf-8'), lang='ja')
    tts_ja.save('ja_speech.mp3')

def remove_files():
    array_files = ['speech.ogg', 'speech.wav', 'en_speech.mp3', 'ja_speech.mp3']
    for f in array_files:
        if os.path.exists(f):
            os.remove(f)
