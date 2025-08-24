# Holy Books Facts Checker - Offline Version

## 🚀 Quick Start (No OpenAI API Required)

Since your OpenAI API quota has been exceeded, you can use the **offline version** that works without any API calls!

### 1. Run the Offline Version

```bash
python app_offline.py
```

### 2. Open Your Browser

Go to: `http://localhost:5001`

### 3. Start Fact Checking!

The offline version provides:
- ✅ **Local scripture search** using vector embeddings
- ✅ **Keyword matching** for relevant verses
- ✅ **Rule-based claim classification**
- ✅ **Citation extraction** from claims
- ✅ **History tracking** in local database
- ✅ **No API costs** - completely free!

## 🔧 How It Works

### Local Analysis Features:
1. **Scripture Search**: Uses FAISS vector database to find relevant verses
2. **Keyword Matching**: Matches claim keywords against scripture text
3. **Reference Extraction**: Automatically finds scripture references (e.g., "Bhagavad Gita 2:47")
4. **Claim Classification**: Rule-based classification into textual/historical/theological
5. **Local Database**: Stores all fact checks locally

### Example Claims to Try:
- "Does Bhagavad Gita 2:47 say that outcomes don't matter?"
- "What does the Quran say about charity?"
- "Does the Bible mention peacemakers?"

## 📊 Limitations

The offline version has some limitations compared to the AI-powered version:
- **No AI analysis** - uses rule-based matching instead
- **Limited scripture data** - only includes sample verses
- **Basic classification** - keyword-based rather than AI-powered
- **No advanced reasoning** - cannot provide detailed theological analysis

## 🔄 Switching Back to AI Version

When your OpenAI API quota resets or you upgrade your plan:

1. **Check your quota**: `python check_openai_status.py`
2. **Run the full version**: `python app.py`
3. **Access at**: `http://localhost:5000`

## 📁 Files

- `app_offline.py` - Offline version (port 5001)
- `app.py` - Full version with OpenAI (port 5000)
- `check_openai_status.py` - Check API status
- `data/` - Scripture data files
- `templates/` - Web interface
- `static/` - CSS and JavaScript

## 🆘 Troubleshooting

### If the offline version doesn't work:
1. Make sure all dependencies are installed: `pip install -r requirements.txt`
2. Check if port 5001 is available
3. Try a different port by editing `app_offline.py`

### To check OpenAI status:
```bash
python check_openai_status.py
```

## 💡 Tips

1. **Be specific** in your claims for better matches
2. **Include scripture references** like "Bhagavad Gita 2:47"
3. **Use keywords** that appear in the sample verses
4. **Check the history** to see previous fact checks

## 🎯 Next Steps

1. **Add more scripture data** to `data/` folder
2. **Upgrade OpenAI plan** for full AI analysis
3. **Customize the interface** in `templates/index.html`
4. **Add more religions** and texts

---

**Enjoy fact-checking without any API costs!** 🎉
