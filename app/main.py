"""
youtube-watching
"""

import os
from http.cookiejar import MozillaCookieJar
import json
import re
import requests
from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

def yt_history(cookie_path):
    """
    get latest video from youtube history excluding reel shelf (shorts)
    """

    # COOKIES
    if not os.path.exists(cookie_path):
        return _error(f"Cookie path '{cookie_path}' does not exist")

    cookie_jar = MozillaCookieJar(cookie_path)

    try:
        cookie_jar.load(ignore_discard=True, ignore_expires=True)
    except Exception as error:
        return _error(f"Failed to load cookies from '{cookie_path}': {error}")

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
    try:
        response = session.get("https://www.youtube.com/feed/history")

    except Exception as error:
        return _error(f"Error fetching YouTube history: {error}")

    cookie_jar.save(ignore_discard=True, ignore_expires=True)
    html = response.text

    # REGEX
    try:
        regex = r"var ytInitialData = (.*);<\/script>"
        match = re.search(regex, html).group(1)

    except Exception as error:
        return _error(f"Failed to extract JSON using regex: {error}")

    # JSON
    try:
        data = json.loads(match)

    except Exception as error:
        return _error(f"Failed to parse JSON: {error}")

    # DATA
    try:
        path = data["contents"]["twoColumnBrowseResultsRenderer"]\
            ["tabs"][0]["tabRenderer"]["content"]["sectionListRenderer"]\
            ["contents"][0]["itemSectionRenderer"]["contents"]

    except Exception as error:
        return _error(f"Failed to extract data: {error}")

    try:
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

    except Exception as error:
        return _error(f"Failed to extract video details from YouTube data: {error}, {path}")

def thumbnail(fid):
    """
    return max resolution
    """

    url = f"https://img.youtube.com/vi/{fid}"
    maxres = f"{url}/maxresdefault.jpg"
    default = f"{url}/0.jpg"

    if requests.get(maxres, timeout=3).status_code == 200:
        return maxres

    return default

def _error(error_msg):
    """
    Log and return error
    """
    print(error_msg)

    return {
        "error": error_msg
    }, 500


class RestApi(Resource):
    """
    https://flask-restful.readthedocs.io/en/latest/quickstart.html
    """

    def get(self):
        """
        on GET request call yt_history
        """

        cookie = os.environ.get('COOKIE')

        if not cookie:
            return _error("COOKIE environment variable not set")

        try:
            return yt_history(cookie)

        except Exception as error:
            return _error(f"Unhandled error occurred: {error}")


api.add_resource(RestApi, "/")

if __name__ == "__main__":
    try:
        from waitress import serve
        serve(app, host="0.0.0.0", port=5678)

    except Exception as error:
        _error(f"Server error: {error}")
