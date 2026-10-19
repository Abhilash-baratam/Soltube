import os
import re
import json
import time
import urllib.request
import yt_dlp
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types

load_dotenv()

app = Flask(__name__)
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

TARGET_MODEL = 'gemini-3.8-flash'

def extract_video_id(url):
    pattern = r'(?:v=|\/|youtu\.be\/)([0-9A-Za-z_-]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def safe_decode_json_str(raw_str):
    """Safely decodes escaped JSON strings without unicode-escape codec crashes."""
    try:
        # Wrap in quotes and parse through standard JSON parser
        clean = raw_str.replace('\\"', '"').replace('"', '\\"')
        return json.loads(f'"{clean}"')
    except Exception:
        # Fallback to direct ASCII cleanup
        return re.sub(r'\\u[0-9a-fA-F]{4}', '', raw_str)

def get_video_info_fallback(video_id):
    """Browser fallback if yt-dlp gets rate-limited by YouTube (HTTP 429)"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    url = f"https://www.youtube.com/watch?v={video_id}"
    resp = requests.get(url, headers=headers, timeout=10)
    page_text = resp.text

    title_match = re.search(r'<title>(.*?)</title>', page_text)
    title = title_match.group(1).replace(" - YouTube", "") if title_match else "YouTube Lecture"

    desc_match = re.search(r'"shortDescription":"(.*?)"', page_text)
    description = ""
    if desc_match:
        description = safe_decode_json_str(desc_match.group(1))

    return title, description, "15 minutes"

def get_youtube_transcript_and_info(url):
    video_id = extract_video_id(url)

    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['en', 'te', 'hi'],
        'quiet': True,
        'no_warnings': True,
        'socket_timeout': 10,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Lecture')
            duration_secs = info.get('duration', 0)
            minutes = int(duration_secs // 60) if duration_secs else 10
            duration_str = f"{minutes} minutes"

            subtitles = info.get('subtitles') or info.get('automatic_captions') or {}
            transcript_text = ""

            chosen_track = None
            for lang in ['en', 'te', 'hi']:
                if lang in subtitles:
                    chosen_track = subtitles[lang]
                    break

            if not chosen_track and subtitles:
                chosen_track = list(subtitles.values())[0]

            if chosen_track:
                track_url = None
                for fmt in chosen_track:
                    if fmt.get('ext') == 'json3':
                        track_url = fmt.get('url')
                        break
                if not track_url and chosen_track:
                    track_url = chosen_track[0].get('url')

                if track_url:
                    req = urllib.request.Request(track_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        raw_data = resp.read().decode('utf-8')
                        try:
                            parsed = json.loads(raw_data)
                            events = parsed.get('events', [])
                            text_parts = []
                            for ev in events:
                                for seg in ev.get('segs', []):
                                    text_parts.append(seg.get('utf8', ''))
                            transcript_text = " ".join("".join(text_parts).split())
                        except Exception:
                            transcript_text = re.sub(r'<[^>]+>', '', raw_data)

            if not transcript_text or len(transcript_text.strip()) < 50:
                description = info.get('description', '')
                transcript_text = f"Title: {title}. Description: {description}"

            return title, transcript_text, duration_str

    except Exception as e:
        print(f"[Notice] yt-dlp warning: {e}. Switching to safe browser fallback...")
        if video_id:
            title, desc, duration_str = get_video_info_fallback(video_id)
            return title, f"Title: {title}. Context and Overview: {desc}", duration_str
        raise e

MASTER_PROMPT = """
You are an expert educator, mentor, and clear communicator. Your goal is to transform this lecture content into a comprehensive, highly accessible study guide that anyone can understand and master instantly.

VIDEO TITLE: {TITLE}
VIDEO DURATION: {VIDEO_DURATION}
LECTURE CONTENT & CONTEXT:
\"\"\"
{TRANSCRIPT}
\"\"\"

---

### INSTRUCTIONS & OUTPUT SPECIFICATIONS:

#### 1. Tone & Formatting Rules
- Use natural, crystal-clear, everyday English. Speak like an encouraging teacher explaining a topic over coffee.
- Divide everything cleanly into distinct block-wise sections.
- Make all explanation headings bold: e.g., **Key Concept:** or **Why This Matters:**.
- Highlight every real-world example with **Real-Life Example:**.
- Avoid robotic conversational filler, meta-announcements, or mentions of reading grade levels.

#### 2. Adaptive Depth Based on Video Duration
- **The Big Picture:** 2 to 3 sentences answering "What is this about and why does it matter to you?"
- **Complete Lesson Breakdown:** Structured sections with bold subheadings, clean bullet points, and practical everyday analogies.
- **Core Concept Quiz:** Exactly 3 to 5 high-yield multiple-choice questions.

#### 3. High-Yield Quiz Rules
- Select ONLY questions that test genuine understanding of core principles.
- Provide 4 distinct options (A, B, C, D) for each question with 1 unambiguously correct answer.
- Make all question titles bold (e.g., **Question 1: ...**).
- Provide a clear, 1-to-2 sentence explanation clarifying why the correct option is right.

---

### OUTPUT FORMAT (Deliver strictly in this markdown structure):

# {TITLE}
**Duration:** {VIDEO_DURATION} | **Level:** [Beginner / Intermediate / Advanced]

---

## 📌 Section 1: The Big Picture
**Overview:** [2-3 clear sentences answering what this topic is and why it matters]

---

## 📖 Section 2: Complete Lesson Breakdown
[Structured notes divided block by block, using bold headings for every subsection and bold highlights for Real-Life Examples]

---

## 🧠 Section 3: Core Concept Quiz

### **Question 1: [High-yield concept question]**
- A) [Option A]
- B) [Option B]
- C) [Option C]
- D) [Option D]
- **Correct Answer:** [Letter]
- **Why it's right:** [1-2 sentences of simple, crystal-clear explanation]
"""

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json() or {}
    url = data.get("url", "").strip()

    if not url or ("youtube.com" not in url and "youtu.be" not in url):
        return jsonify({"error": "Please paste a valid YouTube URL."}), 400

    try:
        title, transcript, duration_str = get_youtube_transcript_and_info(url)

        prompt = MASTER_PROMPT.format(
            TITLE=title,
            VIDEO_DURATION=duration_str,
            TRANSCRIPT=transcript[:25000]
        )

        fast_config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            temperature=0.3
        )

        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=TARGET_MODEL,
                    contents=prompt,
                    config=fast_config
                )
                if response and response.text:
                    return jsonify({"markdown": response.text})
            except Exception as e:
                err_str = str(e)
                if "503" in err_str or "429" in err_str or "UNAVAILABLE" in err_str:
                    time.sleep(2 * (attempt + 1))
                    continue
                return jsonify({"error": err_str}), 500

        return jsonify({"error": "Google API traffic spike. Please retry in 5 seconds."}), 503

    except Exception as e:
        print(f"[FATAL BACKEND ERROR]: {str(e)}")
        return jsonify({"error": f"Failed to extract video: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
