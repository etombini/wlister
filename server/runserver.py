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


@app.route('/parameters_in/')
def page07():
    if 'var1' in request.args and \
            'val1' in request.args.getlist('var1'):
        var1 = True
    if 'var2' in request.args and \
            'val2' in request.args.getlist('var2'):
        var2 = True
    if var1 and var2:
        return 'OK'
    else:
        return 'KO'


@app.route('/content_url_encoded_in/', methods=['POST'])
def page08():
    if 'var1' in request.form and \
            'val1' in request.form.getlist('var1'):
        var1 = True
    if 'var2' in request.form and \
            'val2' in request.form.getlist('var2'):
        var2 = True
    if var1 and var2:
        return 'OK'
    else:
        return 'KO'


@app.route('/headers_in/')
def page09():
    if 'header-test' in request.headers and \
            'test' in request.headers.getlist('header-test'):
        return 'OK'


@app.route('/parameters_list_in/')
def page10():
    if 'var1' in request.args:
        var1 = True
    if 'var2' in request.args:
        var2 = True
    if var1 and var2:
        return 'OK'
    else:
        return 'KO'

@app.route('/headers_list_in/')
def page11():
    if 'listed_in01' in request.headers and \
            'listed_in02' in request.headers:
        return 'OK'
    else:
        return 'KO'

@app.route('/content_url_encoded_list_in/', methods=['POST'])
def page12():
    if 'var1' in request.form and \
            'var2' in request.form:
        return 'OK'
    else:
        return 'KO'

@app.route('/parameters_unique/')
def page13():
    if 'var1' in request.args and \
            len(request.args.getlist('var1')) == 1:
        var1= True
    if 'var2' in request.args and \
            len(request.args.getlist('var2')) == 1:
        var2= True
    if var1 and var2:
        return 'OK'
    else:
        return 'KO'

@app.route('/headers_unique/')
def page14():
    if 'header-test' in request.headers and \
            len(request.headers.getlist('header-test')) == 1:
        return 'OK'
    else:
        return 'KO'

@app.route('/content_url_encoded_unique/', methods=['POST'])
def page15():
    if 'var1' in request.form and \
            len(request.form.getlist('var1')) == 1:
        var1 = True
    if 'var2' in request.form and \
            len(request.form.getlist('var2')) == 1:
        var2 = True
    if var1 and var2:
        return 'OK'
    else:
        return 'KO'

@app.route('/parameters_all_unique/')
def page16():
        return 'OK'

@app.route('/headers_all_unique/')
def page17():
        return 'OK'

@app.route('/content_url_encoded_all_unique/', methods=['POST'])
def page18():
        return 'OK'


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
