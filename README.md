# Interview AI Coach

> **Your AI-powered personal interview practice assistant!**

---

## 🚀 Overview
Interview AI Coach is a beautiful, interactive web application built with [Streamlit](https://streamlit.io/) that helps you prepare for job interviews with AI-generated questions and real-time feedback. Whether you're a junior or senior candidate, this app adapts to your skill level and job title, simulating a real interview experience.

---

## ✨ Features
- **Secure Access:** Password-protected entry to keep your sessions private.
- **Adaptive Questions:** AI-generated questions tailored to your job title and seniority.
- **Instant Feedback:** Receive actionable, AI-driven feedback on your answers.
- **Progress Tracking:** Track your questions, answers, and feedback in a session.
- **Easy Setup:** Minimal configuration with environment variables.

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/InterviewAICoach.git
   cd InterviewAICoach
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   - Copy `.env.example` to `.env` and fill in the required values:
     - `OPENAI_API_KEY` (Get one from [OpenAI](https://platform.openai.com/account/api-keys))
     - `MODEL_PROVIDER` (e.g., `openai`)
     - `MODEL_NAME` (e.g., `gpt-3.5-turbo`)
     - `APP_PASSWORD` (Set your app password)

4. **Run the app:**
   ```bash
   streamlit run app.py
   ```

---

## ⚙️ Usage
1. Enter the password to access the app.
2. Set your job title and seniority level.
3. Start your interview session!
4. Answer questions, receive feedback, and improve your performance.

---

## 📂 Project Structure
```
InterviewAICoach/
├── app.py              # Main Streamlit app
├── ai_helpers.py       # AI logic and helpers
├── requirements.txt    # Python dependencies
├── .env.example        # Example environment variables
├── LICENSSE            # License file
└── ...
```

---

## 🔒 Security & Privacy
- All sessions are password-protected.
- No user data is stored or shared externally.

---

## 🤖 Built With
- [Streamlit](https://streamlit.io/)
- [OpenAI API](https://platform.openai.com/docs/api-reference)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [docoreai](https://pypi.org/project/docoreai/)

---

## 📄 License
This project is licensed under the terms described in the `LICENSSE` file.

---

## 💡 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## 📫 Contact
For support or questions, please open an issue or contact [mailto:abkk70686@gmail.com].

---

*Made with ❤️ by AB*
