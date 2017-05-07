# coding: utf-8

import bs4
import re
from flask import Flask, Response, request
import requests

app = Flask(__name__)

TARGET_PATTERN = re.compile(r"\b(\w{6})\b", re.U)
TARGET_HOST = 'habrahabr.ru'


@app.route('/')
@app.route('/<path:url>')
def home(url=''):
    url = 'https://%s/%s' % (TARGET_HOST, url) \
        if not url.startswith('http') else url

    resp = requests.request(
        method=request.method,
        url=url,
        headers={key: value for (key, value) in
                 request.headers if key != 'Host'},
        cookies=request.cookies
    )

    excluded_headers = ['content-encoding',
                        'content-length',
                        'transfer-encoding',
                        'connection']

    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]

    # it's a html page?
    if resp.headers.get('content-type') == 'text/html; charset=UTF-8':
        soup = bs4.BeautifulSoup(resp.content, 'html.parser')

        # replace links
        for a in soup.findAll('a',
                              href=re.compile('^https://%s' % TARGET_HOST)):
            a['href'] = a['href'].replace("https://%s" % TARGET_HOST, '')

        # let's find an article
        for article in soup.findAll('div', {'class': 'post'}):
            # now let's find a text block inside the article which contains of
            #  words with certain length
            for text_block in article.findAll(text=TARGET_PATTERN):
                # and using lambda with re.sub trying to modify these words in
                # each text block
                modified_text_block = re.sub(
                    TARGET_PATTERN, lambda x: x.group() + '\u2122',
                    text_block.string
                )
                # replace the old block
                text_block.replace_with(modified_text_block)

        return Response(soup.encode(formatter=None), resp.status_code, headers)

    return Response(resp.content, resp.status_code, headers)


if __name__ == '__main__':
    app.run()
