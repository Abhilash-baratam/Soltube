# Soltube – AI-Powered YouTube Study Guide Generator

## About the Project

Soltube is a Python-based application that helps students learn from YouTube educational videos. It uses Google Gemini AI to turn available video captions and information into simple, organized study material.

Instead of going through all the content again, learners can use Soltube to get structured notes, clear explanations, and practice questions.

## Features

- **YouTube Video Input:** Enter a YouTube video URL.
- **Video Content Extraction:** Retrieves available captions and video information.
- **AI-Generated Notes:** Creates structured study material using Google Gemini.
- **Simple Explanations:** Presents concepts in easy-to-understand English.
- **Practice Quiz:** Generates multiple-choice questions to help test understanding.
- **Error Handling:** Includes fallback handling for certain video extraction and API errors.

## How It Works

1. Paste a valid YouTube video link.
2. The application extracts available video information and captions.
3. The extracted content is sent to Google Gemini AI.
4. The AI generates organized notes, explanations, and quiz questions.
5. Review the generated study guide and use it for revision.

## Technology Stack

- Python
- Flask
- Google Gemini API
- yt-dlp
- HTML templates
- Requests and Python dotenv

## Response Time

Generating a study guide may take some time because the application needs to extract video information and process the content using an AI model. The response time can vary depending on video availability, caption extraction, API response time, and service availability.

## Project Goal

The goal of Soltube is to make learning from educational videos easier by turning video content into organized and useful study material.

## Repository

GitHub: https://github.com/Abhilash-baratam/Soltube
