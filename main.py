from wsgiref.simple_server import make_server
from urllib.parse import parse_qs
from html import escape
import re
import os
import db_scripts


def add_comment(environ, start_response):
    if environ['REQUEST_METHOD'] == 'POST':
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except ValueError:
            request_body_size = 0
        request_body = environ['wsgi.input'].read(request_body_size)
        d = parse_qs(request_body.decode())
        comment = {}
        comment['surname'] = escape(d.get('surname')[0])
        comment['name'] = escape(d.get('name')[0])
        comment['patronymic'] = escape(d.get('patronymic', [None])[0]) if 'patronymic' in d else None
        comment['region'] = escape(d.get('region')[0]) if int(d.get('region')[0]) else None
        comment['city'] = escape(d.get('city')[0]) if int(d.get('city')[0]) else None
        comment['phone'] = escape(d.get('phone', [None])[0]) if 'phone' in d else None
        comment['email'] = escape(d.get('email', [None])[0]) if 'email' in d else None
        comment['content'] = escape(d.get('content')[0])

        if db_scripts.add_comment(**comment):
            status = '201 CREATED'
            response_body = 'Коммендарий успешно добавлен'.encode()
        else:
            status = '500 Internal Server Error'
            response_body = 'При добавлении комментария произошла ошибка'.encode()
        response_headers = [
            ('Content-Type', 'text/plain; charset=utf-8'),
            ('Content-Length', str(len(response_body)))
        ]
        start_response(status, response_headers)
        return [response_body]

    regions = db_scripts.get_regions()

    template_path = os.getcwd() + '/templates/new_comment.html'
    with open(template_path, 'r') as f:
        html = f.read()
    html = html % {
        'regions': ''.join([f'<option value={r[0]}>{r[1]}</option>' for r in regions])
    }
    response_body = html.encode()

    status = '200 OK'

    response_headers = [
        ('Content-Type', 'text/html; charset=utf-8'),
        ('Content-Length', str(len(response_body)))
    ]

    start_response(status, response_headers)
    return [response_body]


def comments(environ, start_response):
    comments = db_scripts.get_comments()
    template_path = os.getcwd() + '/templates/comments.html'
    with open(template_path, 'r') as file:
        html = file.read()
    html = html % {
        'comments': ''.join([f'''<div id="{c[0]}" class="comment"><div class="com-header">
            <div class="user">{' '.join(c[1:4]) if c[3] else ' '.join(c[1:3])}</div>
            <button class="del-btn" value={c[0]} onclick="deleteComment(this.value)">X</button>
            </div><div class="com-content">{c[4]}</div></div>''' for c in comments])
    }
    response_body = html.encode()
    status = '200 OK'
    response_headers = [
        ('Content-Type', 'text/html; charset=utf-8'),
        ('Content-Length', str(len(response_body)))
    ]

    start_response(status, response_headers)
    return [response_body]


def stats(environ, start_response):
    regions = db_scripts.get_stats_regions()
    template_path = os.getcwd() + '/templates/stats.html'
    with open(template_path, 'r') as file:
        html = file.read()
    html = html % {
        'regions': ''.join([f'<li class="item"><a href="{r[0]}">{r[1]}</a><span>{r[2]}</span</li>' for r in regions])
    }
    response_body = html.encode()
    status = '200 OK'
    response_headers = [
        ('Content-Type', 'text/html; charset=utf-8'),
        ('Content-Length', str(len(response_body)))
    ]

    start_response(status, response_headers)
    return [response_body]


def region(environ, start_response):
    region = environ['myapp.url_args'][0].encode('iso-8859-1').decode('utf8')
    cities = db_scripts.get_stats_cities(region)
    template_path = os.getcwd() + '/templates/region.html'
    with open(template_path, 'r') as f:
        html = f.read()
    html = html % {
        'region': region,
        'cities': ''.join([f'<li class="item"><a>{c[0]}</a><span>{c[1]}</span</li>' for c in cities])
    }
    response_body = html.encode('utf-8')
    status = '200 OK'
    response_headers = [
        ('Content-Type', 'text/html; charset=utf-8'),
        ('Content-Length', str(len(response_body)))
    ]

    start_response(status, response_headers)
    return [response_body]


def get_cities(environ, start_response):
    if environ['REQUEST_METHOD'] == 'GET':
        d = parse_qs(environ['QUERY_STRING'])
        region = d.get('region')[0]

        cities = db_scripts.get_cities(region)

        response_body = ''.join([f'<option value={c[0]}>{c[1]}</option>' for c in cities]).encode('utf-8')
        status = '200 OK'
        response_headers = [
            ('Content-Type', 'text/html; charset=utf-8'),
            ('Content-Length', str(len(response_body)))
        ]

        start_response(status, response_headers)
        return [response_body]


def delete_comment(environ, start_response):
    if environ['REQUEST_METHOD'] == 'DELETE':
        d = parse_qs(environ['QUERY_STRING'])
        id = d.get('id')[0]
        if db_scripts.delete_comment(id):
            status = '200 OK'
            response_body = 'Комментарий удалён успешно'.encode()
        else:
            status = '500 Internal Server Error'
            response_body = 'При удалении комментария произошла ошибка'.encode()
        response_headers = [
            ('Content-Type', 'text/plain; charset=utf-8'),
            ('Content-Length', str(len(response_body)))
        ]
        start_response(status, response_headers)
        return [response_body]


def not_found(environ, start_response):
    start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
    return [b'Not found']


URLS = [
    (r'new_comment/$', add_comment),
    (r'comments/$', comments),
    (r'stats/$', stats),
    (r'stats/(.+)$', region),
    (r'ajax/get_cities$', get_cities),
    (r'ajax/delete_comment$', delete_comment)
]


def app(environ, start_response):
    path = environ.get('PATH_INFO', '').lstrip('/')
    for regex, callback in URLS:
        match = re.search(regex, path)
        if match is not None:
            environ['myapp.url_args'] = match.groups()
            return callback(environ, start_response)
    return not_found(environ, start_response)


if __name__ == '__main__':
    if not os.path.isfile('app.db'):
        db_scripts.create_db()
    server = make_server('localhost', 8000, app)
    server.serve_forever()
