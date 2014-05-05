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

@app.route('/1parameter/')
def page04():
    try:
        var = request.args.get('var1')
        if var == 'val1':
            return "OK"
        else:
            return "NOK"
    except:
        return "NOK"

@app.route('/parameter_list/')
def page05():
    if 'var1' in request.args and \
            'var2' in request.args and \
            'var3' in request.args:
        return 'OK'
    else:
        return 'KO'

@app.route('/headers/')
def page06():
    if request.headers['header-test'] == 'test':
        return "OK"
    else:
        return "KO"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
