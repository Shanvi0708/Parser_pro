from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
import string

class TextVectorizer:
    """
    Handles text preprocessing and vectorization for resume-JD matching
    """
    
    def __init__(self, method='tfidf'):
        """
        Initialize vectorizer
        Args:
            method: 'tfidf' or 'count' (TF-IDF is recommended)
        """
        self.method = method
        
        if method == 'tfidf':
            self.vectorizer = TfidfVectorizer(
                lowercase=True,
                stop_words='english',
                ngram_range=(1, 2),  # Unigrams and bigrams
                max_features=5000,    # Limit vocabulary size
                min_df=1,             # Minimum document frequency
                max_df=0.8,           # Maximum document frequency
                sublinear_tf=True     # Use logarithmic term frequency
            )
        else:
            self.vectorizer = CountVectorizer(
                lowercase=True,
                stop_words='english',
                ngram_range=(1, 2),
                max_features=5000
            )
    
    def preprocess_text(self, text):
        """
        Clean and preprocess text before vectorization
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove phone numbers
        text = re.sub(r'\+?\d[\d\s\-\(\)]+\d', '', text)
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove numbers (optional - you might want to keep them)
        # text = re.sub(r'\d+', '', text)
        
        return text
    
    def vectorize_documents(self, documents):
        """
        Convert list of documents to TF-IDF vectors
        Args:
            documents: List of text strings
        Returns:
            Sparse matrix of TF-IDF features
        """
        # Preprocess all documents
        processed_docs = [self.preprocess_text(doc) for doc in documents]
        
        # Fit and transform
        vectors = self.vectorizer.fit_transform(processed_docs)
        
        return vectors
    
    def transform_document(self, document):
        """
        Transform a single document using fitted vectorizer
        """
        processed_doc = self.preprocess_text(document)
        return self.vectorizer.transform([processed_doc])
    
    def calculate_similarity(self, text1, text2):
        """
        Calculate cosine similarity between two texts
        Returns: Similarity score (0-100)
        """
        # Preprocess texts
        processed_text1 = self.preprocess_text(text1)
        processed_text2 = self.preprocess_text(text2)
        
        # Vectorize
        vectors = self.vectorizer.fit_transform([processed_text1, processed_text2])
        
        # Calculate cosine similarity
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        
        # Convert to percentage
        return round(similarity * 100, 2)
    
    def get_top_features(self, text, top_n=10):
        """
        Get the most important features (keywords) from text
        """
        processed_text = self.preprocess_text(text)
        
        # Transform text
        vector = self.vectorizer.fit_transform([processed_text])
        
        # Get feature names
        feature_names = self.vectorizer.get_feature_names_out()
        
        # Get TF-IDF scores
        tfidf_scores = vector.toarray()[0]
        
        # Get top N features
        top_indices = tfidf_scores.argsort()[-top_n:][::-1]
        top_features = [(feature_names[i], tfidf_scores[i]) for i in top_indices]
        
        return top_features
    
    def batch_similarity(self, resume_texts, job_description):
        """
        Calculate similarity between multiple resumes and one JD
        Args:
            resume_texts: List of resume texts
            job_description: Single JD text
        Returns:
            List of similarity scores
        """
        # Preprocess all texts
        processed_resumes = [self.preprocess_text(text) for text in resume_texts]
        processed_jd = self.preprocess_text(job_description)
        
        # Combine all documents
        all_docs = processed_resumes + [processed_jd]
        
        # Vectorize
        vectors = self.vectorizer.fit_transform(all_docs)
        
        # JD vector is the last one
        jd_vector = vectors[-1]
        
        # Calculate similarities with all resumes
        similarities = []
        for i in range(len(resume_texts)):
            sim = cosine_similarity(vectors[i:i+1], jd_vector)[0][0]
            similarities.append(round(sim * 100, 2))
        
        return similarities


# Test the vectorizer
if __name__ == "__main__":
    print("=" * 80)
    print("TESTING TEXT VECTORIZER")
    print("=" * 80)
    
    # Initialize vectorizer
    vectorizer = TextVectorizer(method='tfidf')
    
    # Sample texts
    resume_text = """
    Experienced Python developer with 5 years of experience in machine learning
    and data science. Proficient in TensorFlow, PyTorch, and scikit-learn.
    Built multiple NLP models for text classification and sentiment analysis.
    Strong background in deep learning and neural networks.
    """
    
    jd_text = """
    Looking for a Machine Learning Engineer with experience in NLP and deep learning.
    Must have Python programming skills and experience with TensorFlow or PyTorch.
    Knowledge of text classification and neural networks required.
    """
    
    # Test 1: Calculate similarity
    print("\n📊 TEST 1: Calculating Similarity")
    print("-" * 80)
    similarity = vectorizer.calculate_similarity(resume_text, jd_text)
    print(f"Similarity Score: {similarity}%")
    
    # Test 2: Get top keywords from resume
    print("\n📊 TEST 2: Top Keywords from Resume")
    print("-" * 80)
    top_keywords = vectorizer.get_top_features(resume_text, top_n=10)
    for keyword, score in top_keywords:
        print(f"   {keyword}: {score:.4f}")
    
    # Test 3: Get top keywords from JD
    print("\n📊 TEST 3: Top Keywords from Job Description")
    print("-" * 80)
    jd_keywords = vectorizer.get_top_features(jd_text, top_n=10)
    for keyword, score in jd_keywords:
        print(f"   {keyword}: {score:.4f}")
    
    # Test 4: Batch processing
    print("\n📊 TEST 4: Batch Similarity Calculation")
    print("-" * 80)
    
    resumes = [
        "Python developer with machine learning experience",
        "Java developer with web development skills",
        "Data scientist with NLP and deep learning expertise"
    ]
    
    similarities = vectorizer.batch_similarity(resumes, jd_text)
    
    for i, (resume, sim) in enumerate(zip(resumes, similarities), 1):
        print(f"\nResume {i}: {resume[:50]}...")
        print(f"Similarity: {sim}%")
    
    # Test 5: Preprocessing demonstration
    print("\n📊 TEST 5: Text Preprocessing")
    print("-" * 80)
    
    dirty_text = """
    Contact me at john@email.com or call +1-555-1234.
    Visit my website: https://johndoe.com
    I have 5+ years of experience!!!
    """
    
    clean_text = vectorizer.preprocess_text(dirty_text)
    print(f"Original: {dirty_text}")
    print(f"\nCleaned: {clean_text}")
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS COMPLETED!")
    print("=" * 80)