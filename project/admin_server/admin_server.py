from flask import Flask, render_template, session, g, \
    redirect, url_for, abort, abort, flash

DEBUG = True

app = Flask(__name__)

@app.route('/')
def show_index():
    # Used ajax, because already exist data in javascript
    pictures = [ 
    			{'name': 'pic A'},
    			{'name': 'pic B'},
    			{'name': 'pic C'}
    			]
    templateData = {'title' : 'Face Detector',
    				'pictures': pictures
    				}
    return render_template('index2.html', **templateData)


if __name__ == "__main__":
    app.run(port=5000, debug=True)