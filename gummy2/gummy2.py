import os
from flask import Flask, request, g, redirect, url_for, abort, render_template, flash
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)
app.config.from_object(__name__)

@app.route('/')
def home():
    return render_template('home.html')
