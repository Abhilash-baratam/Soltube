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


### Prerequisites
* Node.js 18+ and `npm` / `pnpm` / `yarn`
* Rust and Cargo (for smart contract development)
* Solana CLI tools and Anchor framework

### Installation

1. Clone the repository:
   ```bash
   git clone [https://github.com/Abhilash-baratam/Soltube.git](https://github.com/Abhilash-baratam/Soltube.git)
   cd Soltube
   
Install client dependencies:

Bash
npm install
Set up environment variables:

Bash
cp .env.example .env.local

# Configure your Solana RPC endpoint (Devnet/Mainnet) and IPFS gateway keys
Running Locally
Start Frontend App:

Bash
npm run dev
Open http://localhost:3000 in your browser.

Anchor Smart Contract (Optional):

Bash
cd anchor-program
anchor build
anchor test

## Repository

GitHub: https://github.com/Abhilash-baratam/Soltube
