import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse

import utils


def get_outer_html(url: str):
    """
    URLからページのouterHTMLを取得する

    Params
    ---
    url: str
        ex: https://www.google.com/

    Returns
    ---
    outerHTML: str
        ex: <html>...</html>
        ex: ''
    """
    if isinstance(url, str) is False:
        return ''
    if url in 'https://example.com':
        return ''
    if not url.startswith('http'):
        return ''

    parsed_url = urlparse(url)

    utils.gray_log(f'{parsed_url.netloc}から詳細情報取得開始...')

    response = None
    try:
        # URLからページのHTMLを取得
        response = requests.get(url, timeout=10)
    except Exception:
        return ''

    if response is None:
        return ''

    # ステータスコードが正常でない場合はNoneを返すなどのエラーハンドリングを行うことができます
    if response.status_code != 200:
        return ''

    # BeautifulSoupを使ってHTMLをパース
    soup = BeautifulSoup(response.content, 'html.parser')

    # styleタグを全て削除
    for style in soup.find_all('style'):
        style.decompose()
    # scriptタグを全て削除
    for script in soup.find_all('script'):
        script.decompose()
    # linkタグを全て削除
    for link in soup.find_all('link'):
        link.decompose()
    # noscriptタグを全て削除
    for noscript in soup.find_all('noscript'):
        noscript.decompose()
    # pictureタグを全て削除
    for picture in soup.find_all('picture'):
        picture.decompose()
    # classを削除
    for tag in soup.find_all(True):
        tag.attrs = {}

    outer_html = str(soup)
    outer_html = re.sub(r"<!--(.*?)-->", '', outer_html)

    # outerHTMLを取得して返す
    return outer_html
