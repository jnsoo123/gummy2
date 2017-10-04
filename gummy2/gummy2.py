import os
import sqlite3
from flask import Flask, request, g, redirect, url_for, abort, render_template, flash, jsonify
from flask_bootstrap import Bootstrap
from translate import Translator
import urllib
import speech_recognition as sr
import subprocess as sp

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

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())

@app.cli.command('initdb')
def initdb_command():
    init_db()
    print('Database initialized.')

@app.route('/')
def home():
    remove_files()
    db = get_db()
    #db.execute('delete from locales')
    #db.commit()
    cur = db.execute('select name, code from locales order by id asc')
    locales = cur.fetchall()
    print locales
    return render_template('home.html', locales=locales)

@app.route('/_check_locale', methods=['GET'])
def check_locale():
    language_name = request.args.get('language_name', '', type=str)
    language_locale = request.args.get('language_locale', '', type=str)
    translate = Translator(from_lang='en-US', to_lang=language_locale)
    try:
        translated_text = translate.translate('test')
    except TypeError:
        return jsonify('invalid')

    if 'INVALID TARGET LANGUAGE' in translated_text:
        return jsonify('invalid')
    else:
        db = get_db()
        db.execute('insert into locales (name, code) values (?, ?)', [language_name, language_locale])
        db.commit()

        cur = db.execute('select name, code from locales order by id asc')
        locales = cur.fetchall()

        return jsonify({ 'data': render_template('home.html', locales=locales) })

@app.route('/_edit_language', methods=['POST'])
def edit_language():
    new_name = request.form.get('editName')
    new_code = request.form.get('editCode')
    old_code = request.form.get('locale')
    
    db = get_db()
    db.execute('update locales set name = ?, code = ? where code = ?', [new_name, new_code, old_code])
    db.commit()

    cur = db.execute('select name, code from locales order by id asc')
    locales = cur.fetchall()

    return jsonify({ 'data': render_template('home.html', locales=locales) })

@app.route('/_remove_language', methods=['POST'])
def remove_language():
    locale = request.form.get('locale')
    print locale

    db = get_db()
    db.execute('delete from locales where code = ?', [locale])
    db.commit()

    cur = db.execute('select name, code from locales order by id asc')
    locales = cur.fetchall()

    return jsonify({ 'data': render_template('home.html', locales=locales) })

@app.route('/_translate', methods=['GET'])
def translate():
    remove_files()

    text = request.args.get('text', '', type=unicode)
    lang_to = request.args.get('lang_to', '', type=str)
    lang_from = request.args.get('lang_from', '', type=str)

    print request.args
    
    translate = Translator(to_lang=lang_to, from_lang=lang_from)
    print text

    try:
        translated_text = translate.translate(text)
    except KeyError:
        try:
            translated_text = translate.translate(str(text))
        except UnicodeEncodeError:
            translated_text = urllib.quote(translate.translate(text.encode('utf-8')))
    except UnicodeEncodeError:
        translated_text = urllib.quote(translate.translate(text.encode('utf-8')))

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

def remove_files():
    array_files = ['speech.ogg', 'speech.wav', 'en_speech.mp3', 'ja_speech.mp3']
    for f in array_files:
        if os.path.exists(f):
            os.remove(f)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
