#!/usr/bin/env python3
"""
Minimal Flask test
"""

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello World!'

@app.route('/test')
def test():
    return 'Test endpoint working!'

if __name__ == '__main__':
    print("Starting minimal Flask app...")
    app.run(debug=True, host='127.0.0.1', port=8000)
