from flask import Flask, render_template, session, g, \
    redirect, url_for, abort, abort, flash

DEBUG = True

app = Flask(__name__)

@app.route('/')
def show_index():
    # Used ajax, because already exist data in javascript
    templateData = {'title' : 'Face Detector'}
    return render_template('index.html', **templateData)


if __name__ == "__main__":
    app.run(port=5000, debug=True)