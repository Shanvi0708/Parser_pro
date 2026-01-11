import streamlit as st
import pandas as pd
from matcher import CandidateMatcher
import tempfile
import os
import shutil

# Page config
st.set_page_config(
    page_title="AI Resume Screening System",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .score-high {
        background-color: #d4edda;
        padding: 10px;
        border-radius: 5px;
        border-left: 5px solid #28a745;
    }
    .score-medium {
        background-color: #fff3cd;
        padding: 10px;
        border-radius: 5px;
        border-left: 5px solid #ffc107;
    }
    .score-low {
        background-color: #f8d7da;
        padding: 10px;
        border-radius: 5px;
        border-left: 5px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)

# Initialize matcher
if 'matcher' not in st.session_state:
    st.session_state.matcher = CandidateMatcher()

# Header
st.markdown('<h1 class="main-header">🤖 AI Resume Screening System</h1>', unsafe_allow_html=True)
st.markdown("### Intelligent candidate matching powered by NLP & Machine Learning")

# Sidebar
with st.sidebar:
    st.markdown("## 📊 About")
    st.info("""
    This system uses:
    - **NLP**: Text analysis with spaCy
    - **TF-IDF**: Text vectorization
    - **ML**: Cosine similarity matching
    
    **Features:**
    - Automated resume parsing
    - Skill matching
    - Experience validation
    - Intelligent ranking
    """)
    
    st.markdown("---")
    st.markdown("### 📊 Scoring Weights")
    st.write("- Skills Match: 50%")
    st.write("- Text Similarity: 30%")
    st.write("- Experience: 20%")

# Main content
tab1, tab2, tab3 = st.tabs(["📤 Upload & Analyze", "📊 Results", "ℹ️ How It Works"])

with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📁 Upload Resumes")
        uploaded_files = st.file_uploader(
            "Upload candidate resumes (PDF or DOCX)",
            type=['pdf', 'docx'],
            accept_multiple_files=True,
            help="You can upload multiple files at once"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} resume(s) uploaded")
            for file in uploaded_files:
                st.write(f"- {file.name}")
    
    with col2:
        st.markdown("### 📋 Job Description")
        jd_input_method = st.radio(
            "Choose input method:",
            ["Paste Text", "Upload File"],
            horizontal=True
        )
        
        job_description = ""
        
        if jd_input_method == "Paste Text":
            job_description = st.text_area(
                "Paste job description here:",
                height=200,
                placeholder="Enter the job requirements, required skills, experience, etc..."
            )
        else:
            jd_file = st.file_uploader(
                "Upload job description file",
                type=['txt'],
                help="Upload a .txt file with job description"
            )
            if jd_file:
                job_description = jd_file.read().decode('utf-8')
                st.text_area("Job Description Preview:", job_description, height=200)
    
    st.markdown("---")
    
    # Analyze button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.button("🔍 Analyze Candidates", type="primary", use_container_width=True)
    
    if analyze_button:
        if not uploaded_files:
            st.error("⚠️ Please upload at least one resume!")
        elif not job_description:
            st.error("⚠️ Please provide a job description!")
        else:
            with st.spinner("🔄 Processing resumes... This may take a moment..."):
                results = []
                
                # Create temp directory for processing
                temp_dir = tempfile.mkdtemp()
                
                try:
                    # Save JD to temp file
                    jd_path = os.path.join(temp_dir, "job_description.txt")
                    with open(jd_path, 'w', encoding='utf-8') as f:
                        f.write(job_description)
                    
                    # Process each resume
                    progress_bar = st.progress(0)
                    for idx, uploaded_file in enumerate(uploaded_files):
                        # Save resume to temp file
                        resume_path = os.path.join(temp_dir, uploaded_file.name)
                        with open(resume_path, 'wb') as f:
                            f.write(uploaded_file.getbuffer())
                        
                        # Match candidate
                        try:
                            result = st.session_state.matcher.match_candidate(resume_path, jd_path)
                            results.append(result)
                        except Exception as e:
                            st.warning(f"⚠️ Error processing {uploaded_file.name}: {str(e)}")
                        
                        progress_bar.progress((idx + 1) / len(uploaded_files))
                    
                    # Sort by score
                    results.sort(key=lambda x: x['overall_score'], reverse=True)
                    
                    # Store in session state
                    st.session_state.results = results
                    st.session_state.processed = True
                    
                    st.success(f"✅ Successfully analyzed {len(results)} candidate(s)!")
                    st.balloons()
                    
                finally:
                    # Cleanup temp files
                    shutil.rmtree(temp_dir, ignore_errors=True)

with tab2:
    if 'processed' in st.session_state and st.session_state.processed:
        results = st.session_state.results
        
        # Summary stats
        st.markdown("## 📈 Summary Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        total = len(results)
        strong = len([r for r in results if r['overall_score'] >= 75])
        good = len([r for r in results if 60 <= r['overall_score'] < 75])
        weak = len([r for r in results if r['overall_score'] < 60])
        
        col1.metric("Total Candidates", total)
        col2.metric("🟢 Strong Match", strong)
        col3.metric("🟡 Good Match", good)
        col4.metric("🔴 Weak Match", weak)
        
        st.markdown("---")
        
        # Detailed results
        st.markdown("## 🏆 Candidate Rankings")
        
        for idx, result in enumerate(results, 1):
            score = result['overall_score']
            
            # Determine CSS class based on score
            if score >= 75:
                css_class = "score-high"
                emoji = "🟢"
            elif score >= 60:
                css_class = "score-medium"
                emoji = "🟡"
            else:
                css_class = "score-low"
                emoji = "🔴"
            
            with st.container():
                st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"### {emoji} Rank #{idx}: {result['candidate_name']}")
                    st.write(f"**Email:** {result.get('email', 'N/A') or 'N/A'} | **Phone:** {result.get('phone', 'N/A') or 'N/A'}")
                    st.write(f"**Education:** {result.get('education', 'N/A')} | **Experience:** {result.get('experience_years', 0)} years")
                
                with col2:
                    st.metric("Overall Score", f"{score}%")
                
                # Expandable details
                with st.expander("📊 View Detailed Analysis"):
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Skills Match", f"{result['skill_match_percentage']}%")
                    col2.metric("Text Similarity", f"{result['text_similarity']}%")
                    col3.metric("Experience Match", f"{result.get('experience_match', 0)}%")
                    
                    st.markdown("**✅ Matched Skills:**")
                    if result.get('matched_skills'):
                        st.write(", ".join(result['matched_skills']))
                    else:
                        st.write("None")
                    
                    st.markdown("**❌ Missing Skills:**")
                    if result.get('missing_skills'):
                        st.write(", ".join(result['missing_skills']))
                    else:
                        st.write("None")
                    
                    st.info(result.get('recommendation', 'No recommendation available'))
                
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("---")
        
        # Download results
        st.markdown("## 📥 Export Results")
        
        # Prepare DataFrame
        df_data = []
        for idx, r in enumerate(results, 1):
            df_data.append({
                'Rank': idx,
                'Candidate': r['candidate_name'],
                'Email': r.get('email', 'N/A'),
                'Overall Score': f"{r['overall_score']}%",
                'Skills Match': f"{r['skill_match_percentage']}%",
                'Text Similarity': f"{r['text_similarity']}%",
                'Experience': r.get('experience_years', 0),
                'Recommendation': r.get('recommendation', 'N/A')
            })
        
        df = pd.DataFrame(df_data)
        
        csv = df.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="📥 Download Results as CSV",
            data=csv,
            file_name="candidate_rankings.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    else:
        st.info("👈 Upload resumes and analyze candidates to see results here!")

with tab3:
    st.markdown("## 🔍 How It Works")
    
    st.markdown("""
    ### The AI Resume Screening Process
    
    #### 1️⃣ **Resume Parsing**
    - Extracts text from PDF/DOCX files
    - Identifies contact information (email, phone)
    - Extracts skills using keyword matching
    - Calculates years of experience
    - Determines education level
    
    #### 2️⃣ **Text Vectorization**
    - Preprocesses text (lowercasing, removing stopwords)
    - Creates TF-IDF vectors with unigrams and bigrams
    - Converts text into numerical features
    
    #### 3️⃣ **Similarity Calculation**
    - Computes cosine similarity between resume and JD
    - Measures how closely the candidate matches the job
    
    #### 4️⃣ **Multi-Factor Scoring**
    - **Skills Match (50% weight)**: Percentage of required skills found
    - **Text Similarity (30% weight)**: TF-IDF cosine similarity
    - **Experience Match (20% weight)**: Years of experience comparison
    
    #### 5️⃣ **Intelligent Ranking**
    - Sorts candidates by overall score
    - Provides hiring recommendations:
      - 🟢 **75%+** = Strong Match (Schedule Interview)
      - 🟡 **60-74%** = Good Match (Review Carefully)
      - 🔴 **<60%** = Weak Match (Not Recommended)
    
    ---
    
    ### 🛠️ Technology Stack
    
    - **Python** - Core programming language
    - **spaCy** - Natural Language Processing
    - **scikit-learn** - Machine Learning (TF-IDF, Cosine Similarity)
    - **Streamlit** - Web interface
    - **pandas** - Data processing
    
    ---
    
    ### 📚 About This Project
    
    This system demonstrates:
    - NLP and text processing skills
    - Machine Learning implementation
    - Full-stack development capabilities
    - Problem-solving in HR tech domain
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    Made with ❤️ using Python, NLP, and Machine Learning
</div>
""", unsafe_allow_html=True)