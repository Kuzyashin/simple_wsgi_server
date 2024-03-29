import re
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server
from html import escape
from string import Template


def index(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    with open('./templates/index_page.html') as template_file:
        template = Template(template_file.read())

    return [bytes(template.substitute(), encoding='utf-8')]


def hello(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except ValueError:
        request_body_size = 0
    request_body = environ['wsgi.input'].read(request_body_size)
    d = parse_qs(request_body.decode('utf-8'))
    name = escape(d.get('name', [''])[0])
    phone = escape(d.get('phone', [''])[0])
    with open('./templates/name_phone.html') as template_file:
        template = Template(template_file.read())
    return [bytes(template.substitute({
        'name': name or 'Empty',
        'phone': phone or 'Empty',
    }), encoding='utf-8')]


def not_found(environ, start_response):
    start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
    return [bytes('Not Found', encoding='utf-8')]


def serve_static_css(environ, start_response, file):
    try:
        with open('static/{}'.format(file.split('/')[-1]), 'rb') as f:
            file_data = f.read()
            start_response('200 OK', [('Content-Type', 'text/css')])
            return [file_data]
    except FileNotFoundError:
        return not_found(environ, start_response)


def serve_static_img(environ, start_response, file):
    try:
        with open('static/{}'.format(file).split('/')[-1], 'rb') as f:
            file_data = f.read()
            start_response('200 OK', [('Content-Type', 'text/image/jpeg')])
            return [file_data]
    except FileNotFoundError:
        return not_found(environ, start_response)


urls = [
    (r'^$', index),
    (r'name_phone/?$', hello),
]

files = [
    (r'.*\.jpe?g', serve_static_img),
    (r'.*\.css', serve_static_css)
]


def application(environ, start_response):
    path = environ.get('PATH_INFO', '').lstrip('/')
    for regex, callback in urls:
        match = re.search(regex, path)
        if match is not None:
            return callback(environ, start_response)
    for regex, callback in files:
        match = re.search(regex, path)
        if match is not None:
            return callback(environ, start_response, path)
    return not_found(environ, start_response)


httpd = make_server('', 8123, application)
print("Serving on port 8123...")
httpd.serve_forever()
