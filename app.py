from flask import Flask, render_template, request, jsonify
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__, static_folder='static', template_folder='templates')

# Load dataset
df = pd.read_csv("cleaned_food_dataset3.csv")
df['all ingridients'] = df['all ingridients'].astype(str).apply(lambda x: ' '.join(x.split(', ')))

# TF-IDF and similarity setup
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(df['all ingridients'])
cosine_sim = cosine_similarity(tfidf_matrix)

df['Food Product'] = df['Food Product'].str.strip().str.lower()
indices = pd.Series(df.index, index=df['Food Product']).drop_duplicates()

def get_recommendations(food_product):
    food_product = food_product.strip().lower()
    if food_product not in indices: return []
    idx = indices[food_product]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:6]
    recommended_indices = [i[0] for i in sim_scores]
    unique_recommendations = df['Food Product'].iloc[recommended_indices].drop_duplicates().tolist()
    return unique_recommendations[:5]  # Ensure only top 5 unique recommendations

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    food = request.form.get('food_name', '').strip()
    print(f"Received food name: {food}")  # Debugging
    recommendations = get_recommendations(food)
    print(f"Recommendations: {recommendations}")  # Debugging
    ingredients = df.loc[df['Food Product'] == food, 'all ingridients'].values[0] if food in df['Food Product'].values else "No ingredients found"
    print(f"Ingredients: {ingredients}")  # Debugging
    return jsonify({'recommendations': recommendations, 'ingredients': ingredients})
if __name__ == '__main__':
    app.run(debug=True)