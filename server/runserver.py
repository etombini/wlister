# -*- coding: utf-8 -*-

from flask import Flask, render_template, request

app = Flask('headers', template_folder='templates')


@app.errorhandler(404)
def page_not_found(error):
    return '404'


@app.route('/')
def index():
    return "OK"


@app.route('/int/<int:value>')
def index01(value):
    return "OK"


@app.route('/abc')
def index02():
    return "MUST BE BLACKLISTED"


@app.route('/<arg1>/<arg2>', methods=['GET', 'POST', 'HEAD', 'PUT', 'DELETE'])
def page01(arg1, arg2):
    #return str("<code>" + str(request.__dict__) + "</code>")
    return render_template('headers.html',
                           request=request,
                           arg1=arg1,
                           arg2=arg2)


@app.route('/parameters')
def page02():
    return "OK"


@app.route('/post/', methods=['POST'])
def page03():
    # must get url encoded parameters var1=val1&var2=val2 exactly
    # anything else must return an awful error
    if len(request.form) != 2:
        return "KO - not only 2 parameters - " + str(request.form)
    try:
        if request.form['var1'] != 'val1':
            return
    except:
        return "oups"
    r = "OK - " + str(request.form)
    return r

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
