import os
from flask import Flask, request, g, redirect, url_for, abort, render_template, flash, jsonify
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

@app.route('/_ja_translate', methods=['GET'])
def ja_translate():
    text = request.args.get('text', '', type=str)
    translate = Translator(to_lang='ja', from_lang='en-US')
    translated_text = translate.translate(text)
    return jsonify(translated_text)

@app.route('/_en_translate', methods=['GET'])
def en_translate():
    text = request.args.get('text', '', type=unicode)
    translate = Translator(to_lang='en-US', from_lang='ja')
    translated_text = urllib.quote(translate.translate(text.encode('utf-8')))
    return jsonify(translated_text)

