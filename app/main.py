"""
youtube-watching
"""

import os
import sys
from http.cookiejar import MozillaCookieJar
import json
import re
import requests
from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)


def yt_history(cookie):
    """
    get latest video from youtube history excluding reel shelf (shorts)
    """

    # COOKIES
    cookie_path = os.environ.get('COOKIE')
    if not os.path.exists(cookie_path):
        print(f"ERROR: Cookie file {cookie_path} does not exist")
        return {
            "error": f"Cookie file {cookie_path} does not exist"
        }, 500

    cookie_jar = MozillaCookieJar(cookie)

    try:
        cookie_jar.load(ignore_discard=True, ignore_expires=True)

    except OSError as notfound_error:
        print(f"WARNING: {cookie} not found\nDEBUG: {notfound_error}")
        sys.exit()

    # SESSION
    session = requests.Session()
    session.headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)\
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-us,en;q=0.5",
        "Sec-Fetch-Mode": "navigate",
    }
    session.cookies = cookie_jar

    # RESPONSE
    response = session.get("https://www.youtube.com/feed/history")
    cookie_jar.save(ignore_discard=True, ignore_expires=True)
    html = response.text

    # JSON
    try:
        regex = r"var ytInitialData = (.*);<\/script>"
        match = re.search(regex, html).group(1)
        data = json.loads(match)

        path = data["contents"]["twoColumnBrowseResultsRenderer"]\
            ["tabs"][0]["tabRenderer"]["content"]["sectionListRenderer"]\
            ["contents"][0]["itemSectionRenderer"]["contents"]

    except AttributeError as data_error:
        print(f"WARNING: Can't find data, update cookie file\nDEBUG: {data_error}")
        sys.exit()

    # THUMBNAIL
    def thumbnail(fid):
        """ return max resolution """

        url = f"https://img.youtube.com/vi/{fid}"
        maxres = f"{url}/maxresdefault.jpg"
        default = f"{url}/0.jpg"

        if requests.get(maxres, timeout=3).status_code == 200:
            return maxres

        return default

    # OUTPUT
    if "reelShelfRenderer" in path[0]:
        key = path[1]["videoRenderer"]
    else:
        key = path[0]["videoRenderer"]

    return {
        "channel": key["longBylineText"]["runs"][0]["text"],
        "title": key["title"]["runs"][0]["text"],
        "video_id": key["videoId"],
        "duration_string": key["lengthText"]["simpleText"],
        "thumbnail": thumbnail(key["videoId"]),
        "original_url": f"https://www.youtube.com/watch?v={key['videoId']}",
    }


class RestApi(Resource):
    """
    https://flask-restful.readthedocs.io/en/latest/quickstart.html
    """

    def get(self):
        """
        on GET request run yt_history
        """
        return yt_history(os.environ['COOKIE'])


api.add_resource(RestApi, "/")

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5678)
