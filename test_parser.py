from Parser.resume_parser import ResumeParser
import os

parser = ResumeParser()

# Test on one resume first
resume_path = "data/resumes/resume.pdf"  # Change to your actual file name
result = parser.parse_resume(resume_path)


print("EXTRACTED INFORMATION:")
print(f"\n📧 Email: {result['email']}")
print(f"📞 Phone: {result['phone']}")
print(f"🎓 Education: {result['education']}")
print(f"⏱️  Experience: {result['experience_years']} years")
print(f"\n💼 Skills Found ({len(result['skills'])}):")
for skill in result['skills']:
    print(f"   ✓ {skill}")

print("RAW RESUME TEXT (first 500 chars):")
print(result['raw_text'][:500])
print("...\n")

# Now manually compare
print("MANUAL CHECK:")
print("   Look at the resume text above and answer:")
print("   1. Are all visible skills captured?")
print("   2. Are there false positives (skills not in resume)?")
print("   3. Is the text extraction clean or garbled?")