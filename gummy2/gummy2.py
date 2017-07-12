import os
from flask import Flask, request, g, redirect, url_for, abort, render_template, flash
from flask_bootstrap import Bootstrap
from translate import Translator
import urllib

app = Flask(__name__)
Bootstrap(app)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config.from_object(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/ja_translate', methods=['POST'])
def ja_translate():
    text = request.form['text_translate'].encode('utf-8')
    translate = Translator(to_lang='ja', from_lang='en-US')
    translated_text = translate.translate(text)
    return render_template('home.html', translated_ja_text=translated_text, translated_en_text=text)

@app.route('/en_translate', methods=['POST'])
def en_translate():
    text = request.form['text_translate']
    translate = Translator(to_lang='en-US', from_lang='ja')
    translated_text = urllib.quote(translate.translate(text.encode('utf-8')))
    return render_template('home.html', translated_en_text=translated_text, translated_ja_text=text)

