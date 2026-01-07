from Parser.resume_parser import ResumeParser
from Parser.job_description_parser import JobDescriptionParser
from text_vectorizer import TextVectorizer

class CandidateMatcher:
    def __init__(self):
        self.resume_parser = ResumeParser()
        self.jd_parser = JobDescriptionParser()
        self.vectorizer = TextVectorizer(method='tfidf')
    
    def calculate_skill_match_score(self, candidate_skills, required_skills):
        """Calculate percentage of required skills candidate has"""
        if not required_skills:
            return {
                'percentage': 0.0,
                'matched_skills': [],
                'missing_skills': []
            }
        
        candidate_skills_lower = [s.lower() for s in candidate_skills]
        required_skills_lower = [s.lower() for s in required_skills]
        
        matched_skills = [skill for skill in required_skills_lower 
                         if skill in candidate_skills_lower]
        
        missing_skills = [skill for skill in required_skills_lower 
                         if skill not in candidate_skills_lower]
        
        match_percentage = (len(matched_skills) / len(required_skills_lower)) * 100
        
        return {
            'percentage': round(match_percentage, 2),
            'matched_skills': matched_skills,
            'missing_skills': missing_skills
        }
    
    def calculate_text_similarity(self, resume_text, jd_text):
        """Calculate cosine similarity using TextVectorizer"""
        return self.vectorizer.calculate_similarity(resume_text, jd_text)
    
    def calculate_experience_match(self, candidate_exp, required_exp):
        """Score based on experience match"""
        if required_exp == 0:
            return 100.0
        
        if candidate_exp >= required_exp:
            return 100.0
        elif candidate_exp >= required_exp * 0.7:
            return 70.0
        else:
            return (candidate_exp / required_exp) * 50
    
    def calculate_overall_score(self, skill_match, text_similarity, exp_match):
        """Weighted overall score"""
        weights = {
            'skills': 0.5,      # 50% weight
            'similarity': 0.3,  # 30% weight
            'experience': 0.2   # 20% weight
        }
        
        overall = (
            skill_match * weights['skills'] +
            text_similarity * weights['similarity'] +
            exp_match * weights['experience']
        )
        
        return round(overall, 2)
    
    def get_recommendation(self, overall_score):
        """Get hiring recommendation based on score"""
        if overall_score >= 75:
            return "🟢 STRONG MATCH - Schedule Interview"
        elif overall_score >= 60:
            return "🟡 GOOD MATCH - Review Carefully"
        elif overall_score >= 40:
            return "🟠 POSSIBLE MATCH - Consider for Junior Role"
        else:
            return "🔴 WEAK MATCH - Not Recommended"
    
    def match_candidate(self, resume_path, jd_path):
        """Match a single candidate to a job description"""
        print(f"Processing: {resume_path}")
        
        # Parse resume and JD
        resume_data = self.resume_parser.parse_resume(resume_path)
        jd_data = self.jd_parser.parse_job_description(jd_path)
        
        # Calculate individual scores
        skill_match = self.calculate_skill_match_score(
            resume_data['skills'], 
            jd_data['required_skills']
        )
        
        text_similarity = self.calculate_text_similarity(
            resume_data['raw_text'],
            jd_data['raw_text']
        )
        
        exp_match = self.calculate_experience_match(
            resume_data['experience_years'],
            jd_data['required_experience']
        )
        
        overall_score = self.calculate_overall_score(
            skill_match['percentage'],
            text_similarity,
            exp_match
        )
        
        recommendation = self.get_recommendation(overall_score)
        
        return {
            'candidate_name': resume_path.split('/')[-1].split('\\')[-1],  # Works on both Linux/Windows
            'email': resume_data['email'],
            'phone': resume_data['phone'],
            'education': resume_data['education'],
            'experience_years': resume_data['experience_years'],
            'overall_score': overall_score,
            'skill_match_percentage': skill_match['percentage'],
            'text_similarity': text_similarity,
            'experience_match': exp_match,
            'matched_skills': skill_match['matched_skills'],
            'missing_skills': skill_match['missing_skills'],
            'recommendation': recommendation
        }
    
    def rank_candidates(self, resume_folder, jd_path):
        """Rank all candidates for a job"""
        import os
        
        candidates = []
        
        print("\n" + "=" * 80)
        print("🔄 PROCESSING CANDIDATES")
        print("=" * 80)
        
        for filename in os.listdir(resume_folder):
            if filename.endswith(('.pdf', '.docx')):
                resume_path = os.path.join(resume_folder, filename)
                try:
                    result = self.match_candidate(resume_path, jd_path)
                    candidates.append(result)
                    print(f"✅ {filename}: {result['overall_score']}%")
                except Exception as e:
                    print(f"❌ Error processing {filename}: {e}")
        
        # Sort by overall score (highest first)
        candidates.sort(key=lambda x: x['overall_score'], reverse=True)
        
        print(f"\n✅ Processed {len(candidates)} candidates")
        
        return candidates


# Test the matcher
if __name__ == "__main__":
    print("=" * 80)
    print("TESTING CANDIDATE MATCHER")
    print("=" * 80)
    
    matcher = CandidateMatcher()
    
    # Test single match
    try:
        result = matcher.match_candidate(
            "data/resumes/resume.pdf",
            "data/job_descriptions/jd1.txt"
        )
        
        print("\n" + "=" * 80)
        print("📄 CANDIDATE ANALYSIS")
        print("=" * 80)
        print(f"\nCandidate: {result['candidate_name']}")
        print(f"📧 Email: {result['email']}")
        print(f"📞 Phone: {result['phone']}")
        print(f"🎓 Education: {result['education']}")
        print(f"⏱️  Experience: {result['experience_years']} years")
        
        print("\n" + "=" * 80)
        print(f"🎯 OVERALL SCORE: {result['overall_score']}%")
        print("=" * 80)
        print(f"💼 Skill Match: {result['skill_match_percentage']}%")
        print(f"📝 Text Similarity: {result['text_similarity']}%")
        print(f"⏱️  Experience Match: {result['experience_match']}%")
        
        print(f"\n✅ Matched Skills ({len(result['matched_skills'])}):")
        if result['matched_skills']:
            for skill in result['matched_skills']:
                print(f"   • {skill}")
        else:
            print("   None")
        
        print(f"\n❌ Missing Skills ({len(result['missing_skills'])}):")
        if result['missing_skills']:
            for skill in result['missing_skills']:
                print(f"   • {skill}")
        else:
            print("   None")
        
        print(f"\n{result['recommendation']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you have:")
        print("  1. data/resumes/resume.pdf")
        print("  2. data/job_descriptions/jd1.txt")

