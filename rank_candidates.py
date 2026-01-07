from matcher import CandidateMatcher
import json
import os

def display_rankings(candidates):
    """Display ranked candidates in a nice format"""
    print("\n" + "=" * 100)
    print("🏆 CANDIDATE RANKINGS - SORTED BY SCORE")
    print("=" * 100)
    
    if not candidates:
        print("\n❌ No candidates found!")
        return
    
    for i, candidate in enumerate(candidates, 1):
        print(f"\n{'=' * 100}")
        print(f"RANK #{i} | Overall Score: {candidate['overall_score']}% | {candidate['candidate_name']}")
        print('=' * 100)
        
        # Contact & Basic Info
        print(f"📧 {candidate['email'] or 'N/A'} | 📞 {candidate['phone'] or 'N/A'}")
        print(f"🎓 {candidate['education']} | ⏱️  {candidate['experience_years']} years experience")
        
        # Score Breakdown
        print(f"\n📊 Score Breakdown:")
        print(f"   • Skills Match:     {candidate['skill_match_percentage']}%")
        print(f"   • Text Similarity:  {candidate['text_similarity']}%")
        print(f"   • Experience Match: {candidate['experience_match']}%")
        
        # Matched Skills
        if candidate['matched_skills']:
            skills_display = ', '.join(candidate['matched_skills'][:8])
            print(f"\n✅ Has Required Skills ({len(candidate['matched_skills'])}):")
            print(f"   {skills_display}")
            if len(candidate['matched_skills']) > 8:
                print(f"   ... and {len(candidate['matched_skills']) - 8} more")
        else:
            print(f"\n✅ Has Required Skills: None")
        
        # Missing Skills
        if candidate['missing_skills']:
            missing_display = ', '.join(candidate['missing_skills'][:5])
            print(f"\n❌ Missing Skills ({len(candidate['missing_skills'])}):")
            print(f"   {missing_display}")
            if len(candidate['missing_skills']) > 5:
                print(f"   ... and {len(candidate['missing_skills']) - 5} more")
        
        # Recommendation
        print(f"\n💡 {candidate['recommendation']}")
    
    # Summary Statistics
    print("\n" + "=" * 100)
    print("📈 SUMMARY STATISTICS")
    print("=" * 100)
    
    total = len(candidates)
    strong = len([c for c in candidates if c['overall_score'] >= 75])
    good = len([c for c in candidates if 60 <= c['overall_score'] < 75])
    possible = len([c for c in candidates if 40 <= c['overall_score'] < 60])
    weak = len([c for c in candidates if c['overall_score'] < 40])
    
    print(f"\n📊 Total Candidates Analyzed: {total}")
    print(f"\n🟢 Strong Matches:   {strong:2d} ({strong/total*100:5.1f}%) - Schedule Interview")
    print(f"🟡 Good Matches:     {good:2d} ({good/total*100:5.1f}%) - Review Carefully")
    print(f"🟠 Possible Matches: {possible:2d} ({possible/total*100:5.1f}%) - Consider for Junior")
    print(f"🔴 Weak Matches:     {weak:2d} ({weak/total*100:5.1f}%) - Not Recommended")
    
    # Top 3 candidates
    print("\n" + "=" * 100)
    print("⭐ TOP 3 CANDIDATES TO INTERVIEW")
    print("=" * 100)
    
    for i, candidate in enumerate(candidates[:3], 1):
        print(f"{i}. {candidate['candidate_name']} - {candidate['overall_score']}% - {candidate['email']}")

def save_results_to_json(candidates, output_file="ranking_results.json"):
    """Save results to JSON file"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(candidates, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Full results saved to: {output_file}")

def save_results_to_csv(candidates, output_file="ranking_results.csv"):
    """Save results to CSV file"""
    import csv
    
    if not candidates:
        print("No candidates to save!")
        return
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'rank', 'candidate_name', 'overall_score', 
            'skill_match_percentage', 'text_similarity', 'experience_match',
            'email', 'phone', 'education', 'experience_years',
            'matched_skills', 'missing_skills', 'recommendation'
        ]
        
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for i, candidate in enumerate(candidates, 1):
            row = candidate.copy()
            row['rank'] = i
            row['matched_skills'] = ', '.join(row['matched_skills'])
            row['missing_skills'] = ', '.join(row['missing_skills'])
            writer.writerow(row)
    
    print(f"📊 Results exported to CSV: {output_file}")

def analyze_skill_gaps(candidates):
    """Analyze common missing skills across all candidates"""
    print("\n" + "=" * 100)
    print("🔍 SKILL GAP ANALYSIS")
    print("=" * 100)
    
    all_missing = {}
    
    for candidate in candidates:
        for skill in candidate['missing_skills']:
            all_missing[skill] = all_missing.get(skill, 0) + 1
    
    if all_missing:
        sorted_missing = sorted(all_missing.items(), key=lambda x: x[1], reverse=True)
        
        print(f"\n❌ Most Commonly Missing Skills:")
        for skill, count in sorted_missing[:10]:
            percentage = (count / len(candidates)) * 100
            print(f"   • {skill}: {count}/{len(candidates)} candidates ({percentage:.0f}%)")
    else:
        print("\n✅ All candidates have all required skills!")

if __name__ == "__main__":
    print("=" * 100)
    print("🚀 AI RESUME SCREENING & CANDIDATE RANKING SYSTEM")
    print("=" * 100)
    
    # Initialize matcher
    matcher = CandidateMatcher()
    
    # Configuration
    RESUMES_FOLDER = "data/resumes"
    JD_FILE = "data/job_descriptions/jd1.txt"
    
    # Check if folders exist
    if not os.path.exists(RESUMES_FOLDER):
        print(f"\n❌ Error: Folder '{RESUMES_FOLDER}' not found!")
        exit(1)
    
    if not os.path.exists(JD_FILE):
        print(f"\n❌ Error: Job description '{JD_FILE}' not found!")
        exit(1)
    
    # Count resumes
    resume_files = [f for f in os.listdir(RESUMES_FOLDER) if f.endswith(('.pdf', '.docx'))]
    print(f"\n📁 Found {len(resume_files)} resumes in '{RESUMES_FOLDER}'")
    print(f"📋 Using job description: '{JD_FILE}'")
    
    # Rank all candidates
    print("\n" + "=" * 100)
    print("🔄 PROCESSING ALL CANDIDATES...")
    print("=" * 100)
    
    candidates = matcher.rank_candidates(RESUMES_FOLDER, JD_FILE)
    
    # Display rankings
    display_rankings(candidates)
    
    # Skill gap analysis
    analyze_skill_gaps(candidates)
    
    # Save results
    print("\n" + "=" * 100)
    print("💾 SAVING RESULTS")
    print("=" * 100)
    
    save_results_to_json(candidates)
    save_results_to_csv(candidates)
    
    print("\n" + "=" * 100)
    print("✅ ANALYSIS COMPLETE!")
    print("=" * 100)
    print("\n📂 Check these files:")
    print("   • ranking_results.json - Full detailed results")
    print("   • ranking_results.csv - Spreadsheet format")
    print("\n🎯 Next Steps:")
    print("   1. Review top candidates")
    print("   2. Schedule interviews with strong matches")
    print("   3. Consider upskilling for common skill gaps")