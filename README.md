# Holy Books Facts Checker

A comprehensive, AI-powered fact-checking application for verifying claims about holy books and religious texts across major world religions. Built with Python Flask and modern web technologies.

## 🌟 Features

### Core Functionality
- **Multi-Faith Support**: Covers Hinduism, Islam, Christianity, Sikhism, Buddhism, and Judaism
- **Text & Voice Input**: Submit claims via typing or voice recording
- **AI-Powered Analysis**: Uses OpenAI GPT models for intelligent fact checking
- **Academic Rigor**: Provides citations, confidence scores, and scholarly perspectives
- **Multi-Language Support**: English, Hindi, Arabic, Hebrew, Sanskrit

### User Interface
- **Modern Web UI**: Clean, responsive design with Tailwind CSS
- **Real-time Results**: Instant fact checking with detailed analysis
- **Accessibility Features**: Dyslexia-friendly fonts, keyboard navigation
- **Export Options**: PDF and JSON export functionality
- **History Tracking**: View and reuse previous fact checks

### Technical Features
- **Vector Search**: FAISS-based similarity search for relevant scriptures
- **Speech Recognition**: Browser-based voice input processing
- **Text-to-Speech**: Audio output of results
- **Database Storage**: SQLite for persistent fact check history
- **RESTful API**: Clean API endpoints for integration

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- OpenAI API key
- Modern web browser with microphone access

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd holy-books-facts-checker
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   FLASK_ENV=development
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open your browser**
   Navigate to `http://localhost:5000`

## 📖 Usage Guide

### Submitting a Claim

1. **Text Input**: Type your claim in the text area
   - Example: "Does Bhagavad Gita 2:47 say that outcomes don't matter?"

2. **Voice Input**: Click the microphone button and speak your claim
   - The system will transcribe your speech to text

3. **Select Language**: Choose your preferred language from the dropdown

4. **Choose Claim Type**: Select from Textual, Historical, or Mixed

5. **Submit**: Click "Check Facts" to analyze your claim

### Understanding Results

The system provides:

- **Verdict**: Supported, Contradicted, Partially Supported, Unclear, or Theological
- **Confidence Score**: 0-100% indicating reliability
- **Rationale**: Detailed explanation of the verdict
- **Citations**: Relevant scripture passages with references
- **Alternative Views**: Different scholarly interpretations
- **Next Steps**: Suggestions for further research

### Export Options

- **PDF Export**: Generate a printable report
- **JSON Export**: Download structured data for analysis
- **Audio Output**: Listen to the results using text-to-speech

## 🏗️ Architecture

### Backend (Python Flask)
```
app.py                 # Main Flask application
├── HolyBooksFactsChecker  # Core fact checking logic
├── API Endpoints      # RESTful API routes
├── Database           # SQLite for data persistence
└── AI Integration     # OpenAI API integration
```

### Frontend (HTML/CSS/JavaScript)
```
templates/
└── index.html         # Main UI template

static/
└── js/
    └── app.js         # Frontend JavaScript logic
```

### Data Structure
```
data/
├── bhagavad_gita.json # Sample scripture data
├── quran.json         # Sample scripture data
└── bible.json         # Sample scripture data
```

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key
- `FLASK_ENV`: Development/production environment
- `FLASK_DEBUG`: Enable/disable debug mode

### Customization
- Add more scripture data in the `data/` directory
- Modify the UI styling in `templates/index.html`
- Extend the fact checking logic in `app.py`

## 📚 Supported Texts

### Hinduism
- Bhagavad Gita (multiple translations)
- Vedas (Rigveda, Samaveda, Yajurveda, Atharvaveda)
- Upanishads
- Ramayana and Mahabharata

### Islam
- Quran (Sahih International, Pickthall, Yusuf Ali translations)
- Major Hadith collections

### Christianity
- Bible (Old and New Testament)
- Multiple translations (KJV, NIV, ESV)

### Sikhism
- Guru Granth Sahib
- Multiple translations

### Buddhism
- Tripitaka (Pali Canon)
- Selected Mahayana sutras

### Judaism
- Tanakh (Hebrew Bible)
- Talmud (relevant sections)

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Development Guidelines
- Follow PEP 8 for Python code
- Use meaningful commit messages
- Add comments for complex logic
- Test thoroughly before submitting

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for providing the GPT models
- The academic community for scripture translations
- Contributors and beta testers
- Respect for all faiths and religious traditions

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed information

## 🔮 Future Enhancements

- [ ] Additional language support
- [ ] Mobile app version
- [ ] Advanced citation analysis
- [ ] Community fact checking
- [ ] Integration with academic databases
- [ ] Real-time collaboration features

---

**Note**: This application is designed to be respectful and academically rigorous. It does not promote any particular religion or belief system, but rather provides tools for understanding and verifying claims about religious texts.
