from flask import Flask, request, jsonify, Blueprint
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import LabelEncoder, StandardScaler
import tensorflow as tf
from tensorflow.keras.models import load_model
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import pickle
import warnings
import os
from flask_cors import cross_origin
warnings.filterwarnings('ignore')

# Download NLTK resources
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt_tab')

# Initialize Flask app
# app = Flask(__name__)

# ================== FUNGSI PREPROCESSING ==================
def preprocess_text(text):
    """Preprocessing teks untuk ekstraksi fitur"""
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    
    if pd.isna(text):
        return ""
    
    text = str(text).lower()
    text = re.sub(r'[^\w\s,]', '', text)
    ingredients = [ingredient.strip() for ingredient in text.split(',')]
    
    tokens = []
    for ingredient in ingredients:
        words = word_tokenize(ingredient)
        words = [lemmatizer.lemmatize(word) for word in words 
                if word not in stop_words and len(word) > 2]
        tokens.extend(words)
    
    return ' '.join(tokens)

def preprocess_dataframe(df):
    """Preprocessing complete dataframe"""
    print("🔄 Memulai preprocessing data...")
    
    df = df.drop_duplicates(subset=['id', 'nama'], keep='first')
    df['deskripsi'] = df['deskripsi'].fillna('')
    
    df['deskripsi_Clean'] = df['deskripsi'].apply(preprocess_text)
    
    le_category = LabelEncoder()
    df['category_Encoded'] = le_category.fit_transform(df['category'])
    
    df['Ingredient_Count'] = df['deskripsi'].apply(lambda x: len(x.split(',')))
    df['Text_Length'] = df['deskripsi_Clean'].apply(len)
    
    print(f"✅ Preprocessing selesai! Dataset shape: {df.shape}")
    return df, le_category

def extract_tfidf_features(df, tfidf_vectorizer, scaler, max_features=1000):
    """Ekstraksi fitur menggunakan TF-IDF"""
    print("🔄 Ekstraksi fitur TF-IDF...")
    
    tfidf_matrix = tfidf_vectorizer.transform(df['deskripsi_Clean']).toarray()
    
    additional_features = df[['category_Encoded', 'Ingredient_Count', 'Text_Length']].values
    additional_features_scaled = scaler.transform(additional_features)
    
    feature_matrix = np.hstack([
        tfidf_matrix,
        additional_features_scaled * 0.3
    ])
    
    print(f"✅ Feature extraction selesai! Feature shape: {feature_matrix.shape}")
    return feature_matrix

# ================== FUNGSI REKOMENDASI ==================
def get_recommendations(food_id, df, cosine_sim_matrix, top_n=5):
    """Dapatkan rekomendasi untuk id tertentu"""
    try:
        idx = df[df['id'] == food_id].index
        if len(idx) == 0:
            return {"error": f"id {food_id} tidak ditemukan."}
        
        idx = idx[0]
        
        sim_scores = list(enumerate(cosine_sim_matrix[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:top_n+1]
        
        food_indices = [i[0] for i in sim_scores]
        similarities = [i[1] for i in sim_scores]
        
        # Ambil data yang akan ditampilkan
        result_df = df.iloc[food_indices][['id', 'nama', 'harga', 'stock', 'category', 'image', 'deskripsi']].copy()
        result_df['Similarity_Score'] = similarities

        # Tambahkan URL gambar default jika image kosong
        DEFAULT_IMAGE_URL = "https://via.placeholder.com/150"
        result_df['image'] = result_df['image'].fillna(DEFAULT_IMAGE_URL)
        result_df['image'] = result_df['image'].replace('', DEFAULT_IMAGE_URL)

        # Convert ke list of dict
        recommendations = result_df.to_dict(orient='records')
        return recommendations
        
    except Exception as e:
        return {"error": str(e)}

# ================== LOAD COMPONENTS ==================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_all_components():
    """Load semua komponen model dengan path absolut"""
    print("🔄 Loading semua komponen...")
    
    try:
        embedding_model_path = os.path.join(BASE_DIR, 'food_embedding_model.h5')
        tfidf_vectorizer_path = os.path.join(BASE_DIR, 'tfidf_vectorizer.pkl')
        scaler_path = os.path.join(BASE_DIR, 'scaler.pkl')
        cosine_sim_matrix_path = os.path.join(BASE_DIR, 'cosine_similarity_matrix.npy')

        embedding_model = load_model(embedding_model_path)
        with open(tfidf_vectorizer_path, 'rb') as f:
            tfidf_vectorizer = pickle.load(f)
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)
        cosine_sim_matrix = np.load(cosine_sim_matrix_path)

        print("✅ Semua komponen berhasil di-load!")
        return embedding_model, tfidf_vectorizer, scaler, cosine_sim_matrix
    except Exception as e:
        raise Exception(f"Error loading components: {str(e)}")

try:
    embedding_model, tfidf_vectorizer, scaler, cosine_sim_matrix = load_all_components()
    dataset_path = os.path.join(BASE_DIR, 'food_dataset.csv')
    df = pd.read_csv(dataset_path)
    df_processed, le_category = preprocess_dataframe(df)
except Exception as e:
    print(f"❌ Failed to load components or dataset: {str(e)}")
    embedding_model, tfidf_vectorizer, scaler, cosine_sim_matrix, df_processed = None, None, None, None, None

# ================== FLASK ENDPOINT ==================
ml_bp = Blueprint('ml', __name__, url_prefix='/ml')

@ml_bp.route('/', methods=['POST'])
@cross_origin(supports_credentials=True)
def recommend():
    """Endpoint untuk mendapatkan rekomendasi berdasarkan id"""
    if any(x is None for x in [embedding_model, tfidf_vectorizer, scaler, cosine_sim_matrix, df_processed]):
        print("❌ Komponen belum di-load dengan benar.")
        return jsonify({"error": "Server initialization failed. Please check server logs."}), 500
    
    try:
        data = request.get_json()
        if not data or 'id' not in data:
            return jsonify({"error": "Missing 'id' in request body"}), 400
        
        food_id = data['id']
        if not isinstance(food_id, int) or food_id < 1:
            return jsonify({"error": "Invalid 'id'. Must be a positive integer."}), 400
        
        recommendations = get_recommendations(food_id, df_processed, cosine_sim_matrix, top_n=5)
        
        if isinstance(recommendations, dict) and "error" in recommendations:
            return jsonify(recommendations), 404
        
        return jsonify({
            "status": "success",
            "id": food_id,
            "recommendations": recommendations
        }), 200
    
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

