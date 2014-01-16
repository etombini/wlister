# -*- coding: utf-8 -*-

from flask import Flask, render_template, request

app = Flask('headers', template_folder='templates')


@app.route('/')
def index():
    return "OK"


@app.route('/<arg1>/<arg2>', methods=['GET', 'POST', 'HEAD', 'PUT', 'DELETE'])
def page01(arg1, arg2):
    #return str("<code>" + str(request.__dict__) + "</code>")
    return render_template('headers.html',
                           request=request,
                           arg1=arg1,
                           arg2=arg2)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
