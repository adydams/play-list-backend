
import requests
from openai import OpenAI;
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv



app = Flask(__name__)
CORS(app)
#Load environment variables from .env file
load_dotenv()

# Access keys as before
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
YOUTUBE_API_KEY = YOUTUBE_API_KEY #"AIzaSyCIx7gbJq5lgQFJ1Yc4vpZ1Qivp6De_3QM"

def get_deepseek_response(prompt, api_key=None, api_base="https://api.deepseek.com"):
    """
    Send a prompt to the DeepSeek chat API and return the generated response.

    :param prompt: A string containing your query or request (e.g. "5 popular rock songs...").
    :param api_key: DeepSeek API key, or None to read from environment variable.
    :param api_base: Base URL for DeepSeek (default https://api.deepseek.com).
    :return: The assistant's text response as a string (empty if none).
    """

    # Fallback to environment variable if api_key isn't provided
    if not api_key:
        api_key = DEEPSEEK_API_KEY

    # Create the DeepSeek-compatible client
    client = OpenAI(api_key=api_key, base_url=api_base)

    # Create a chat completion with the chosen model
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": prompt},
        ],
        stream=False
    )

    if not response.choices:
        return ""

    return response.choices[0].message.content.strip()

def get_youtube_url(song_title, artist):

   
    """Fetches the YouTube URL for a given song using the YouTube Data API."""
    search_query = f"{song_title} {artist}"
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={search_query}&key={YOUTUBE_API_KEY}&type=video"

    response = requests.get(url)
    data = response.json()

    if "items" in data and data["items"]:
          video_id = data["items"][0]["id"]["videoId"]
          # Generate the YouTube link by appending the video ID
          return f"https://www.youtube.com/watch?v={video_id}"

    return None


def get_artist_image(song_title, artist):
    """Fetches an image URL for the given artist using Bing Image Search API."""
    """Fetches the YouTube URL for a given song using the YouTube Data API."""
    search_query= f"{song_title} {artist}"
    print("************")
    print(search_query)
    youtube_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={search_query}&key={YOUTUBE_API_KEY}&type=video"

    response = requests.get(youtube_url)
    data = response.json()

    if "items" in data and data["items"]:
          album_url = data["items"][0]["snippet"]["thumbnails"]["medium"]["url"]
          # Generate the YouTube link by appending the video ID
          return f"{album_url}"

    return None


@app.route('/generate_playlist', methods=['GET'])
def generate_playlist():
    """
    Generate a playlist of songs for a given genre using the DeepSeek REST API.
    Returns JSON in the form:
    {
      "genre": <genre>,
      "playlist": [
        { "title": <title>, "artist": <artist>, "songLink": <songLink>,  "singerPictureLink": <singerPictureLink>, },
        ...
      ]
    }
    """
    genre = request.args.get("genre", "").strip()
    if not genre:
        return jsonify({"error": "Genre parameter is required"}), 400

    # 1. Formulate a prompt for DeepSeek (asking for 5 songs for the given genre).
    prompt = (
        f"Provide a list of 5 popular {genre} songs in the format:\n"
        "1. <song_title> - <artist>\n"
        "2. <song_title> - <artist>\n"
        "3. <song_title> - <artist>\n"
        "4. <song_title> - <artist>\n"
        "5. <song_title> - <artist>\n"
    )

    # 2. Query DeepSeek
    response_text = get_deepseek_response(prompt)

    if not response_text:
        return jsonify({"error": "No text returned from DeepSeek."}), 502

    # 3. Parse the text to extract songs in "Title - Artist" format
    lines = response_text.split("\n")
    playlist = []
    for line in lines:
        if " - " in line:
            # Attempt to remove numbering prefix like "1. "
            if ". " in line:
                line_content = line.split(". ", 1)[-1]
            else:
                line_content = line

            parts = line_content.split(" - ", 1)
            if len(parts) == 2:
                title, artist = parts[0].strip(), parts[1].strip()
                if title and artist:
                    song_url = get_youtube_url(title, artist)
                    artist_image = get_artist_image(title, artist)

                    playlist.append({
                        "title": title,
                        "artist": artist,
                        "songLink": song_url or "Not Found",
                        "singerPictureLink": artist_image or "Not Found",
                    })
    if not playlist:
        return jsonify({"error": "Failed to parse songs from response text"}), 502

    return jsonify({"genre": genre, "playlist": playlist}), 200


if __name__ == '__main__':
    # In production, consider using a server like Gunicorn or uWSGI instead
    app.run(debug=True)



