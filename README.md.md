# 🍽️ FoodAI - Smart Food Recommendation System

[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-Latest-green)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen)]()

> An intelligent AI-powered web application that recommends similar dishes based on ingredients using TF-IDF vectorization and cosine similarity.

## 📸 Features

- ✨ **Smart Food Search** - Find similar dishes using AI-powered recommendations
- 🤖 **FoodBot Chatbot** - Interactive chat interface for food queries
- 🔍 **Auto-Complete** - Smart suggestions as you type
- 📊 **TF-IDF Based Matching** - Content-based recommendation engine
- 🎨 **Beautiful UI** - Modern glass-morphism design with animated backgrounds
- 📱 **Responsive Design** - Works seamlessly on desktop and mobile devices
- 🗂️ **Comprehensive Dataset** - Database of diverse food items with ingredients

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Flask (Python Web Framework) |
| **ML/AI** | Scikit-learn (TF-IDF, Cosine Similarity) |
| **Data** | Pandas (Data Processing) |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Styling** | Custom CSS with Glass-morphism |
| **Icons** | Font Awesome 6.5.0 |
| **Fonts** | Google Fonts (Inter, Poppins) |

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- **Python 3.8+**
- **pip** (Python Package Manager)
- **Virtual Environment** (recommended)

## ⚡ Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/nikhilkumar0811/food-recommendation.git
cd food-recommendation
```

### 2. Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python app.py
```

### 5. Open in Browser
Navigate to `http://localhost:5000` in your web browser

## 📁 Project Structure

```
food-recommendation/
│
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
│
├── cleaned_food_dataset3.csv       # Food items & ingredients dataset
│
├── templates/
│   └── index.html                  # Main web interface
│
└── static/
    ├── css/
    │   └── style.css              # Styling (Glass-morphism design)
    ├── js/
    │   └── script.js              # Frontend logic & interactions
    └── images/
        └── background.avif        # Background imagery
```

## 🚀 How It Works

### 1. **Data Processing**
- Loads food dataset from CSV with ingredients
- Normalizes and cleans food names (lowercase, strip whitespace)
- Removes duplicate entries
- Converts ingredient strings into processable format

### 2. **Recommendation Engine**
- **TF-IDF Vectorization**: Converts ingredient text into numerical vectors
- **Cosine Similarity**: Calculates similarity between food items
- **Ranking**: Sorts results by similarity score (0-100%)

### 3. **Search Pipeline**
```
User Input → Fuzzy Matching → TF-IDF Vectorization → 
Cosine Similarity → Ranking → Top N Results
```

### 4. **Interactive Features**
- **Search**: Find similar dishes based on ingredients
- **Autocomplete**: Real-time food suggestions
- **Chatbot**: Natural language queries about dishes
- **Smart Fallback**: Fuzzy matching for misspellings

## 🎯 Core Algorithms

### Cosine Similarity Matching
```python
similarity = (A · B) / (||A|| × ||B||)
```
Measures angle between ingredient vectors (0 = different, 1 = identical)

### TF-IDF Vectorization
```python
TF-IDF(t, d) = TF(t, d) × log(N / DF(t))
```
Weights ingredients by frequency and importance

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main web interface |
| `/search` | POST | Get food recommendations |
| `/autocomplete` | GET | Get autocomplete suggestions |
| `/chatbot` | POST | Chat with FoodBot |

### Example Request/Response

**Search Request:**
```json
POST /search
{
  "food_name": "pizza"
}
```

**Response:**
```json
{
  "matched": "Pizza",
  "ingredients": "flour, tomato, cheese, herbs",
  "recommendations": [
    {
      "name": "Italian Bread",
      "score": 85.3,
      "ingredients": "flour, yeast, salt, olive oil"
    },
    {
      "name": "Pasta Margherita",
      "score": 78.9,
      "ingredients": "pasta, tomato, mozzarella, basil"
    }
  ]
}
```

## 💡 Key Features Explained

### 1. Fuzzy Matching
Handles user typos gracefully:
- "pizzaa" → "pizza"
- "burgr" → "burger"

### 2. Intelligent Chatbot
Understands various query types:
- **Ingredient queries**: "What's in butter chicken?"
- **Recommendation queries**: "Suggest something like pizza"
- **List queries**: "What foods do you know?"

### 3. Responsive Autocomplete
- Prefix matching: "but" → "butter chicken", "butter naan"
- Substring fallback: "utter" → "butter chicken"
- Shows top 8 suggestions

## 📊 Dataset Information

**File**: `cleaned_food_dataset3.csv`

**Columns**:
- `Food Product`: Name of the food item
- `all ingredients`: Comma-separated list of ingredients

**Statistics**:
- Contains diverse food items (Indian, Italian, Asian, etc.)
- Clean, normalized ingredient data
- Duplicates removed for accuracy

## 🎨 Customization

### Change Port
```python
# app.py (last line)
if __name__ == '__main__':
    app.run(debug=True, port=8080)  # Change port to 8080
```

### Modify Recommendation Count
```python
# app.py (line 39)
def get_recommendations(food_product, top_n=10):  # Change top_n
```

### Update Dataset
Replace `cleaned_food_dataset3.csv` with your own CSV file with columns:
- `Food Product`
- `all ingredients`

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Module not found" | Run `pip install -r requirements.txt` |
| Port already in use | Change port in `app.py` or kill process using port 5000 |
| Food not found | Check dataset, ensure food name exists |
| Slow recommendations | Dataset size is large; consider filtering |

## 📈 Performance Optimization

- **Vectorization**: Pre-computed TF-IDF matrix in memory
- **Indexing**: Pandas Series indexing for O(1) lookups
- **Caching**: Cosine similarity matrix cached at startup
- **Lazy Loading**: Frontend processes suggestions asynchronously

## 🔐 Security Considerations

- Input sanitization on search queries
- Server-side validation for all requests
- No sensitive data in dataset
- CSRF protection ready (can be added)

## 📝 Dependencies

See `requirements.txt` for complete list:
- Flask: Web framework
- Pandas: Data manipulation
- Scikit-learn: ML algorithms
- Werkzeug: WSGI utilities

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Nikhil Kumar**
- GitHub: [@nikhilkumar0811](https://github.com/nikhilkumar0811)
- Email: nikhil.kumr@example.com

## 🌟 Show Your Support

Give a ⭐️ if this project helped you!

## 📞 Support

For support and queries:
- Open an issue on [GitHub Issues](https://github.com/nikhilkumar0811/food-recommendation/issues)
- Email: nikhil.kumr@example.com

---

**Made with ❤️ using Flask & Machine Learning**
