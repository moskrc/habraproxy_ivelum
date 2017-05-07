# coding: utf-8
import re
import bs4

from proxy2 import ProxyRequestHandler, ThreadingHTTPServer

PROXY_PORT = 8000
TARGET_PATTERN = re.compile(r"\b(\w{6})\b", re.U)


class CustomRequestHandler(ProxyRequestHandler):
    cakey = 'ca.key'
    cacert = 'ca.crt'
    certkey = 'cert.key'
    certdir = 'certs/'

    def response_handler(self, req, req_body, res, res_body):

        if req.path.startswith('https://habrahabr.ru/'):
            soup = bs4.BeautifulSoup(res_body)

            # let's find an article
            for article in soup.findAll('div', {"class": "post"}):
                # now let's find a text block inside the article which contains of words with certain length
                for text_block in article.findAll(text=TARGET_PATTERN):
                    # and using lambda with re.sub trying to modify these words in each text block
                    modified_text_block = re.sub(TARGET_PATTERN, lambda x: x.group() + '\u2122', text_block.string)
                    # replace the old block
                    text_block.replace_with(modified_text_block)

            return ('%s' % soup).encode('utf-8')


if __name__ == '__main__':
    CustomRequestHandler.protocol_version = "HTTP/1.1"
    httpd = ThreadingHTTPServer(('', PROXY_PORT), CustomRequestHandler)
    sa = httpd.socket.getsockname()
    print("Serving Proxy on", sa[0], "port", sa[1], "...")
    httpd.serve_forever()
