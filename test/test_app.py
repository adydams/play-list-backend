import unittest
from unittest.mock import patch, MagicMock
from app import app, get_deepseek_response, get_youtube_url, get_artist_image

class TestPlaylistAPI(unittest.TestCase):
    def setUp(self):
        """Set up the Flask test client"""
        self.client = app.test_client()
        self.client.testing = True

    @patch("app.requests.get")
    def test_get_youtube_url(self, mock_get):
        """Test YouTube URL fetching with mocked API response"""
        mock_response = {
            "items": [{"id": {"videoId": "12345"}}]
        }
        mock_get.return_value.json.return_value = mock_response

        url = get_youtube_url("Song Title", "Artist")
        self.assertEqual(url, "https://www.youtube.com/watch?v=12345")

    @patch("app.requests.get")
    def test_get_artist_image(self, mock_get):
        """Test fetching artist image URL with mocked response"""
        mock_response = {
            "items": [{"snippet": {"thumbnails": {"medium": {"url": "http://image.url"}}}}]
        }
        mock_get.return_value.json.return_value = mock_response

        image_url = get_artist_image("Song Title", "Artist")
        self.assertEqual(image_url, "http://image.url")

    @patch("app.OpenAI")
    def test_get_deepseek_response(self, mock_openai):
        """Test DeepSeek API response parsing"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="1. Song - Artist\n2. Song2 - Artist2"))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        response_text = get_deepseek_response("test prompt", api_key="fake_key")
        self.assertIn("1. Song - Artist", response_text)

    @patch("app.get_deepseek_response")
    @patch("app.get_youtube_url")
    @patch("app.get_artist_image")
    def test_generate_playlist(self, mock_get_artist_image, mock_get_youtube_url, mock_deepseek):
        """Test /generate_playlist API"""
        mock_deepseek.return_value = "1. Song1 - Artist1\n2. Song2 - Artist2"
        mock_get_youtube_url.return_value = "https://youtube.com/song1"
        mock_get_artist_image.return_value = "https://image.com/artist1"

        response = self.client.get("/generate_playlist?genre=rock")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn("playlist", data)
        self.assertEqual(len(data["playlist"]), 2)
        self.assertEqual(data["playlist"][0]["songLink"], "https://youtube.com/song1")

    def test_generate_playlist_no_genre(self):
        """Test API error handling when no genre is provided"""
        response = self.client.get("/generate_playlist")
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", data)

if __name__ == "__main__":
    unittest.main()
