import re

class JobDescriptionParser:
    def __init__(self):
        self.skills_database = [
            'python', 'java', 'javascript', 'react', 'sql', 'mongodb',
            'machine learning', 'deep learning', 'nlp', 'tensorflow',
            'pytorch', 'docker', 'kubernetes', 'aws', 'git', 'agile'
        ]
    
    def parse_job_description(self, jd_path):
        """Parse job description from text file"""
        with open(jd_path, 'r', encoding='utf-8') as file:
            text = file.read()
        
        return {
            'raw_text': text,
            'required_skills': self.extract_required_skills(text),
            'required_experience': self.extract_required_experience(text),
        }
    
    def extract_required_skills(self, text):
        """Extract required skills from JD"""
        text_lower = text.lower()
        found_skills = []
        
        for skill in self.skills_database:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def extract_required_experience(self, text):
        """Extract required years of experience"""
        patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'minimum\s+(\d+)\s+years?',
            r'at least\s+(\d+)\s+years?'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return int(matches[0])
        
        return 0

# Test
if __name__ == "__main__":
    parser = JobDescriptionParser()
    jd = parser.parse_job_description("data/job_descriptions/jd1.txt")
    print("Required Skills:", jd['required_skills'])
    print("Required Experience:", jd['required_experience'])