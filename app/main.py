"""
youtube-watching
"""

import os
from flask import Flask
from flask_restful import Resource, Api
import yt_dlp

app = Flask(__name__)
api = Api(app)


def yt_dlp_history(cookie):
    """
    https://github.com/yt-dlp/yt-dlp#embedding-yt-dlp
    """

    url = 'https://www.youtube.com/feed/history'

    ydl_opts = {
        'cookiefile': cookie,
        'playlist_items': '1',
        'quiet': 'true',
        'no_warnings': 'true'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    path = ydl.sanitize_info(info)['entries'][0]

    return {
        "channel": path['channel'],
        "title": path['fulltitle'],
        "video_id": path['id'],
        "duration_string": path['duration_string'],
        "thumbnail": path['thumbnail'],
        "original_url": path['original_url']
    }


class RestApi(Resource):
    """
    https://flask-restful.readthedocs.io/en/latest/quickstart.html
    """

    def get(self):
        """
        on GET request run yt-dlp
        """
        return yt_dlp_history(os.environ['COOKIE'])


api.add_resource(RestApi, "/")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5678)
