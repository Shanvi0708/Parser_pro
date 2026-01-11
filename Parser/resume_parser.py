# this file we:
# 1. Take  a resume file
#3. Read the file
#4. convert into plain text
#5. return the text
import PyPDF2  #to read the pdf resume 
import re      #to find the patterns
import spacy   #for nlp 
from docx import Document 

# Smart model loading with fallback
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("SpaCy model not found. Using blank model.")
    nlp = spacy.blank("en")

class ResumeParser:
    def __init__(self):
        self.skills_database ={
            'python', 'java', 'javascript', 'react', 'sql', 'mongodb',
            'machine learning', 'deep learning', 'nlp', 'tensorflow',
            'pytorch', 'docker', 'kubernetes', 'aws', 'git', 'agile',
            'data analysis', 'pandas', 'numpy', 'scikit-learn'
        }

    def extract_text_from_pdf(self,pdf_path):
        #extract text from pdf
        text = ""
        try:
            with open(pdf_path,'rb') as file:
                pdf_reader  = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
        except Exception as e:
            print(f" Error reading PDF : {e}")
        return text
    
    def extract_text_from_docx(self,docx_path):
        # Extract text from docx
        try:
            doc = Document(docx_path)
            text ="/n".join([para.text for para in doc.paragrpahs])
            return text
        except Exception as e:
            print(f" Error reading docx: {e}")
            return ""
    def extract_contact_info(self, text):
        """Extract email and phone number"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        
        email = re.findall(email_pattern, text)
        phone = re.findall(phone_pattern, text)
        
        return {
            'email': email[0] if email else None,
            'phone': phone[0] if phone else None
        }
    
    def extract_skills(self, text):
        """Extract skills from resume text"""
        text_lower = text.lower()
        found_skills = []
        
        for skill in self.skills_database:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return list(set(found_skills))  # Remove duplicates
    
    def extract_experience_years(self, text):
        """Extract years of experience"""
        # Look for patterns like "5 years", "3+ years", "2-4 years"
        patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'experience\s*:?\s*(\d+)\+?\s*years?',
            r'(\d+)\s*-\s*(\d+)\s*years?'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if isinstance(matches[0], tuple):
                    return int(matches[0][0])  # Return first number
                return int(matches[0])
        
        return 0
    
    def extract_education(self, text):
        """Extract education level"""
        education_keywords = {
            'PhD': ['phd', 'ph.d', 'doctorate'],
            'Masters': ['masters', 'master', 'ms', 'm.s', 'mba', 'm.b.a'],
            'Bachelors': ['bachelors', 'bachelor', 'bs', 'b.s', 'b.tech', 'be', 'b.e']
        }
        
        text_lower = text.lower()
        
        for degree, keywords in education_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return degree
        
        return "Not specified"
    
    def parse_resume(self, file_path):
        """Main parsing function"""
        # Determine file type and extract text
        if file_path.endswith('.pdf'):
            text = self.extract_text_from_pdf(file_path)
        elif file_path.endswith('.docx'):
            text = self.extract_text_from_docx(file_path)
        else:
            return None
        
        # Extract all information
        contact_info = self.extract_contact_info(text)
        skills = self.extract_skills(text)
        experience = self.extract_experience_years(text)
        education = self.extract_education(text)
        
        return {
            'raw_text': text,
            'email': contact_info['email'],
            'phone': contact_info['phone'],
            'skills': skills,
            'experience_years': experience,
            'education': education
        }

# Test the parser
if __name__ == "__main__":
    parser = ResumeParser()
    
    # Test with your resume files
    resume_path = "data/resumes/resume.pdf"
    result = parser.parse_resume(resume_path)
    
    print("=== PARSED RESUME ===")
    print(f"Email: {result['email']}")
    print(f"Phone: {result['phone']}")
    print(f"Skills: {result['skills']}")
    print(f"Experience: {result['experience_years']} years")
    print(f"Education: {result['education']}")    
    