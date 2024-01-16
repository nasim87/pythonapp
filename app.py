from flask import Flask, request, jsonify
import os
import requests
import json
from moviepy.editor import VideoFileClip
import string
import random

app = Flask(__name__)

def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def download_and_convert_to_mp3(video_url):
    fbdlapi_url = f'https://fbdlapi.instafinsta.app/get_video_links?url={video_url}'
    response = requests.get(fbdlapi_url)
    data = json.loads(response.text)

    video_url = data['links'].get('Download High Quality', data['links'].get('Download Low Quality'))

    random_filename = generate_random_string(12) + '.mp4'

    response = requests.get(video_url)
    with open(random_filename, 'wb') as file:
        file.write(response.content)

    mp3_filename = random_filename.replace('.mp4', '.mp3')
    video_clip = VideoFileClip(random_filename)
    video_clip.audio.write_audiofile(mp3_filename, verbose=False)
    video_clip.close()

    mp3_path = os.path.abspath(mp3_filename)

    os.remove(random_filename)

    return mp3_path

@app.route('/convert_to_mp3', methods=['GET'])
def convert_to_mp3():
    video_url = request.args.get('video_url')

    if not video_url:
        return jsonify({"error": "Missing 'video_url' parameter"}), 400

    try:
        mp3_path = download_and_convert_to_mp3(video_url)
        return jsonify({"mp3_path": mp3_path})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
