import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
import spacy
from collections import Counter
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

class ResumeScorer:
    """
    Advanced Resume Scoring System
    
    This class provides comprehensive resume analysis and scoring based on:
    - Content completeness and quality
    - Structure and formatting
    - Industry-specific requirements
    - Action verbs and impact metrics
    - Skills relevance and diversity
    - Professional presentation
    """
    
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Scoring weights for different components
        self.weights = {
            'content_completeness': 0.25,
            'content_quality': 0.20,
            'structure_formatting': 0.15,
            'skills_analysis': 0.15,
            'action_verbs': 0.10,
            'professional_presentation': 0.10,
            'industry_specific': 0.05
        }
        
        # Industry-specific keywords and requirements
        self.industry_keywords = {
            'data_science': [
                'machine learning', 'deep learning', 'python', 'r', 'sql', 'statistics',
                'data analysis', 'data visualization', 'tensorflow', 'pytorch', 'scikit-learn',
                'pandas', 'numpy', 'matplotlib', 'seaborn', 'jupyter', 'git', 'docker',
                'aws', 'azure', 'gcp', 'spark', 'hadoop', 'kafka', 'elasticsearch'
            ],
            'web_development': [
                'javascript', 'python', 'java', 'php', 'html', 'css', 'react', 'angular',
                'vue.js', 'node.js', 'django', 'flask', 'express', 'mongodb', 'mysql',
                'postgresql', 'redis', 'docker', 'kubernetes', 'aws', 'azure', 'git',
                'rest api', 'graphql', 'microservices', 'ci/cd'
            ],
            'mobile_development': [
                'android', 'ios', 'swift', 'kotlin', 'java', 'react native', 'flutter',
                'xamarin', 'objective-c', 'xcode', 'android studio', 'firebase',
                'app store', 'google play', 'mobile ui/ux', 'push notifications'
            ],
            'ui_ux': [
                'figma', 'sketch', 'adobe xd', 'invision', 'prototyping', 'wireframing',
                'user research', 'usability testing', 'information architecture',
                'interaction design', 'visual design', 'design systems', 'responsive design',
                'accessibility', 'user experience', 'user interface'
            ]
        }
        
        # Action verbs that indicate strong achievements
        self.action_verbs = [
            'developed', 'implemented', 'designed', 'created', 'built', 'launched',
            'managed', 'led', 'coordinated', 'optimized', 'improved', 'increased',
            'decreased', 'reduced', 'enhanced', 'streamlined', 'automated', 'deployed',
            'maintained', 'troubleshot', 'analyzed', 'researched', 'collaborated',
            'mentored', 'trained', 'delivered', 'achieved', 'exceeded', 'generated',
            'saved', 'boosted', 'scaled', 'innovated', 'architected', 'engineered'
        ]
        
        # Impact metrics keywords
        self.impact_metrics = [
            'increased', 'decreased', 'reduced', 'improved', 'boosted', 'enhanced',
            'saved', 'generated', 'achieved', 'exceeded', 'scaled', 'optimized',
            'streamlined', 'automated', 'delivered', 'launched', 'built', 'created'
        ]
        
        # Professional presentation indicators
        self.professional_indicators = [
            'consistent formatting', 'clear structure', 'professional language',
            'proper grammar', 'concise writing', 'logical flow', 'relevant content'
        ]
        
        # Required sections for a complete resume
        self.required_sections = [
            'contact information', 'summary', 'objective', 'experience', 'work experience',
            'education', 'skills', 'projects', 'certifications', 'achievements',
            'volunteer', 'languages', 'interests', 'hobbies'
        ]
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess the resume text"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep important ones
        text = re.sub(r'[^\w\s\-\.\,\;\:\!\?\(\)]', '', text)
        
        return text.strip()
    
    def extract_sections(self, text: str) -> Dict[str, str]:
        """Extract different sections from the resume"""
        sections = {}
        
        # Common section headers
        section_patterns = {
            'contact': r'(contact|phone|email|address|location)',
            'summary': r'(summary|profile|objective|about)',
            'experience': r'(experience|work experience|employment|professional experience)',
            'education': r'(education|academic|qualification|degree)',
            'skills': r'(skills|technical skills|competencies|expertise)',
            'projects': r'(projects|portfolio|work samples)',
            'certifications': r'(certifications|certificates|accreditations)',
            'achievements': r'(achievements|awards|recognition|honors)',
            'volunteer': r'(volunteer|volunteering|community service)',
            'languages': r'(languages|language skills)',
            'interests': r'(interests|hobbies|activities)'
        }
        
        lines = text.split('\n')
        current_section = 'general'
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this line is a section header
            section_found = False
            for section_name, pattern in section_patterns.items():
                if re.search(pattern, line, re.IGNORECASE):
                    if current_content:
                        sections[current_section] = ' '.join(current_content)
                    current_section = section_name
                    current_content = []
                    section_found = True
                    break
            
            if not section_found:
                current_content.append(line)
        
        # Add the last section
        if current_content:
            sections[current_section] = ' '.join(current_content)
        
        return sections
    
    def calculate_content_completeness_score(self, sections: Dict[str, str], text: str) -> Tuple[float, Dict]:
        """Calculate score based on content completeness"""
        score = 0
        max_score = 100
        details = {}
        
        # Check for required sections
        found_sections = []
        for section in self.required_sections:
            if any(section in key.lower() for key in sections.keys()):
                found_sections.append(section)
                score += 8  # 8 points per section (100/12 sections ≈ 8)
        
        # Bonus for having all essential sections
        essential_sections = ['contact', 'experience', 'education', 'skills']
        essential_found = sum(1 for section in essential_sections if section in found_sections)
        if essential_found == len(essential_sections):
            score += 10
        
        # Check for contact information completeness
        contact_info = sections.get('contact', '') + sections.get('general', '')
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        
        if re.search(email_pattern, contact_info):
            score += 5
        if re.search(phone_pattern, contact_info):
            score += 5
        
        details['found_sections'] = found_sections
        details['essential_sections_found'] = essential_found
        details['has_email'] = bool(re.search(email_pattern, contact_info))
        details['has_phone'] = bool(re.search(phone_pattern, contact_info))
        
        return min(score, max_score), details
    
    def calculate_content_quality_score(self, sections: Dict[str, str], text: str) -> Tuple[float, Dict]:
        """Calculate score based on content quality"""
        score = 0
        max_score = 100
        details = {}
        
        # Analyze sentence structure and complexity
        sentences = sent_tokenize(text)
        avg_sentence_length = np.mean([len(word_tokenize(sent)) for sent in sentences])
        
        # Optimal sentence length is between 10-20 words
        if 10 <= avg_sentence_length <= 20:
            score += 20
        elif 8 <= avg_sentence_length <= 25:
            score += 15
        elif 5 <= avg_sentence_length <= 30:
            score += 10
        else:
            score += 5
        
        # Check for action verbs in experience section
        experience_text = sections.get('experience', '')
        action_verbs_found = []
        for verb in self.action_verbs:
            if verb in experience_text.lower():
                action_verbs_found.append(verb)
        
        action_verb_score = min(len(action_verbs_found) * 3, 30)
        score += action_verb_score
        
        # Check for impact metrics
        impact_metrics_found = []
        for metric in self.impact_metrics:
            if metric in experience_text.lower():
                impact_metrics_found.append(metric)
        
        impact_score = min(len(impact_metrics_found) * 2, 20)
        score += impact_score
        
        # Check for quantifiable achievements (numbers, percentages)
        numbers_pattern = r'\b\d+(?:\.\d+)?%?\b'
        numbers_found = re.findall(numbers_pattern, experience_text)
        quantifiable_score = min(len(numbers_found) * 2, 20)
        score += quantifiable_score
        
        # Check for professional language
        professional_words = ['collaborated', 'implemented', 'developed', 'managed', 'led', 'achieved']
        professional_count = sum(1 for word in professional_words if word in text.lower())
        professional_score = min(professional_count * 2, 10)
        score += professional_score
        
        details['avg_sentence_length'] = round(avg_sentence_length, 2)
        details['action_verbs_found'] = action_verbs_found
        details['impact_metrics_found'] = impact_metrics_found
        details['quantifiable_achievements'] = len(numbers_found)
        details['professional_language_score'] = professional_score
        
        return min(score, max_score), details
    
    def calculate_structure_formatting_score(self, text: str) -> Tuple[float, Dict]:
        """Calculate score based on structure and formatting"""
        score = 0
        max_score = 100
        details = {}
        
        lines = text.split('\n')
        
        # Check for consistent formatting
        line_lengths = [len(line.strip()) for line in lines if line.strip()]
        if line_lengths:
            avg_line_length = np.mean(line_lengths)
            if 40 <= avg_line_length <= 80:  # Optimal line length
                score += 20
            elif 30 <= avg_line_length <= 100:
                score += 15
            else:
                score += 10
        
        # Check for proper section headers (capitalized, clear)
        header_pattern = r'^[A-Z][A-Z\s]+$'
        headers_found = sum(1 for line in lines if re.match(header_pattern, line.strip()))
        header_score = min(headers_found * 5, 30)
        score += header_score
        
        # Check for bullet points and lists
        bullet_pattern = r'^[\-\*•]\s'
        bullets_found = sum(1 for line in lines if re.match(bullet_pattern, line.strip()))
        bullet_score = min(bullets_found * 2, 20)
        score += bullet_score
        
        # Check for consistent spacing
        empty_lines = sum(1 for line in lines if not line.strip())
        if 0.1 <= empty_lines / len(lines) <= 0.3:  # Good spacing ratio
            score += 15
        else:
            score += 5
        
        # Check for professional formatting
        if any(word in text.lower() for word in ['resume', 'cv', 'curriculum vitae']):
            score += 15
        
        details['avg_line_length'] = round(avg_line_length, 2) if line_lengths else 0
        details['headers_found'] = headers_found
        details['bullets_found'] = bullets_found
        details['spacing_ratio'] = round(empty_lines / len(lines), 2) if lines else 0
        
        return min(score, max_score), details
    
    def calculate_skills_analysis_score(self, sections: Dict[str, str], text: str) -> Tuple[float, Dict]:
        """Calculate score based on skills analysis"""
        score = 0
        max_score = 100
        details = {}
        
        skills_text = sections.get('skills', '')
        if not skills_text:
            skills_text = text  # Fallback to full text
        
        # Count total skills mentioned
        skills_list = re.findall(r'\b[A-Za-z][A-Za-z\s\+#\.]+(?:\+|\s|$)', skills_text)
        total_skills = len([skill.strip() for skill in skills_list if len(skill.strip()) > 2])
        
        # Score based on number of skills (optimal: 10-20 skills)
        if 10 <= total_skills <= 20:
            score += 30
        elif 5 <= total_skills <= 25:
            score += 20
        elif total_skills > 25:
            score += 15
        else:
            score += 5
        
        # Check for technical vs soft skills balance
        technical_keywords = ['python', 'java', 'javascript', 'sql', 'html', 'css', 'react', 'angular', 'node', 'docker', 'aws', 'machine learning', 'data analysis']
        soft_keywords = ['leadership', 'communication', 'teamwork', 'problem solving', 'time management', 'collaboration', 'adaptability']
        
        technical_skills = sum(1 for keyword in technical_keywords if keyword in skills_text.lower())
        soft_skills = sum(1 for keyword in soft_keywords if keyword in skills_text.lower())
        
        # Balance score
        if technical_skills > 0 and soft_skills > 0:
            score += 25
        elif technical_skills > 0 or soft_skills > 0:
            score += 15
        
        # Check for current/relevant skills
        current_skills = ['python', 'javascript', 'react', 'node.js', 'docker', 'kubernetes', 'aws', 'machine learning', 'data science']
        current_skills_found = sum(1 for skill in current_skills if skill in skills_text.lower())
        current_score = min(current_skills_found * 3, 30)
        score += current_score
        
        # Check for skill categorization
        if any(category in skills_text.lower() for category in ['technical', 'soft', 'programming', 'tools', 'languages']):
            score += 15
        
        details['total_skills'] = total_skills
        details['technical_skills'] = technical_skills
        details['soft_skills'] = soft_skills
        details['current_skills_found'] = current_skills_found
        
        return min(score, max_score), details
    
    def calculate_action_verbs_score(self, sections: Dict[str, str]) -> Tuple[float, Dict]:
        """Calculate score based on action verbs usage"""
        score = 0
        max_score = 100
        details = {}
        
        experience_text = sections.get('experience', '')
        if not experience_text:
            return 0, {'action_verbs_found': [], 'impact_verbs_found': []}
        
        # Find action verbs
        found_verbs = []
        for verb in self.action_verbs:
            if verb in experience_text.lower():
                found_verbs.append(verb)
        
        # Score based on number of action verbs
        verb_score = min(len(found_verbs) * 5, 50)
        score += verb_score
        
        # Check for impact verbs specifically
        impact_verbs = [verb for verb in found_verbs if verb in self.impact_metrics]
        impact_score = min(len(impact_verbs) * 3, 30)
        score += impact_score
        
        # Bonus for variety of verbs
        if len(found_verbs) >= 5:
            score += 20
        
        details['action_verbs_found'] = found_verbs
        details['impact_verbs_found'] = impact_verbs
        details['verb_variety_bonus'] = len(found_verbs) >= 5
        
        return min(score, max_score), details
    
    def calculate_professional_presentation_score(self, text: str) -> Tuple[float, Dict]:
        """Calculate score based on professional presentation"""
        score = 0
        max_score = 100
        details = {}
        
        # Check for grammar and spelling (basic check)
        sentences = sent_tokenize(text)
        proper_sentences = 0
        
        for sentence in sentences:
            # Basic grammar check: starts with capital letter, ends with punctuation
            if sentence and sentence[0].isupper() and sentence[-1] in '.!?':
                proper_sentences += 1
        
        grammar_score = min((proper_sentences / len(sentences)) * 40, 40) if sentences else 0
        score += grammar_score
        
        # Check for professional language
        professional_terms = ['collaborated', 'implemented', 'developed', 'managed', 'achieved', 'delivered', 'optimized']
        professional_count = sum(1 for term in professional_terms if term in text.lower())
        professional_score = min(professional_count * 3, 30)
        score += professional_score
        
        # Check for concise writing (avoid redundancy)
        words = word_tokenize(text.lower())
        unique_words = set(words)
        vocabulary_richness = len(unique_words) / len(words) if words else 0
        
        if vocabulary_richness > 0.6:
            score += 20
        elif vocabulary_richness > 0.5:
            score += 15
        else:
            score += 10
        
        # Check for consistent formatting
        lines = text.split('\n')
        consistent_formatting = all(len(line.strip()) <= 100 for line in lines if line.strip())
        if consistent_formatting:
            score += 10
        
        details['grammar_score'] = round(grammar_score, 2)
        details['professional_terms_found'] = professional_count
        details['vocabulary_richness'] = round(vocabulary_richness, 3)
        details['consistent_formatting'] = consistent_formatting
        
        return min(score, max_score), details
    
    def calculate_industry_specific_score(self, sections: Dict[str, str], text: str) -> Tuple[float, Dict]:
        """Calculate score based on industry-specific requirements"""
        score = 0
        max_score = 100
        details = {}
        
        # Determine industry based on skills and content
        industry_scores = {}
        
        for industry, keywords in self.industry_keywords.items():
            keyword_matches = sum(1 for keyword in keywords if keyword in text.lower())
            industry_scores[industry] = keyword_matches
        
        # Find the most relevant industry
        if industry_scores:
            best_industry = max(industry_scores, key=industry_scores.get)
            best_score = industry_scores[best_industry]
            
            # Score based on industry relevance
            if best_score >= 5:
                score += 50
            elif best_score >= 3:
                score += 30
            elif best_score >= 1:
                score += 15
            
            # Check for industry-specific sections
            if best_industry == 'data_science':
                if any(section in text.lower() for section in ['projects', 'research', 'analysis']):
                    score += 25
            elif best_industry == 'web_development':
                if any(section in text.lower() for section in ['projects', 'portfolio', 'deployment']):
                    score += 25
            elif best_industry == 'mobile_development':
                if any(section in text.lower() for section in ['apps', 'mobile', 'ios', 'android']):
                    score += 25
            elif best_industry == 'ui_ux':
                if any(section in text.lower() for section in ['design', 'prototype', 'wireframe']):
                    score += 25
            
            # Bonus for having relevant certifications
            if 'certification' in text.lower() or 'certificate' in text.lower():
                score += 25
        
        details['industry_scores'] = industry_scores
        details['best_industry'] = best_industry if industry_scores else 'unknown'
        details['industry_relevance_score'] = best_score if industry_scores else 0
        
        return min(score, max_score), details
    
    def calculate_overall_score(self, text: str) -> Dict:
        """Calculate the overall resume score with detailed breakdown"""
        # Preprocess text
        processed_text = self.preprocess_text(text)
        
        # Extract sections
        sections = self.extract_sections(processed_text)
        
        # Calculate individual component scores
        completeness_score, completeness_details = self.calculate_content_completeness_score(sections, processed_text)
        quality_score, quality_details = self.calculate_content_quality_score(sections, processed_text)
        structure_score, structure_details = self.calculate_structure_formatting_score(processed_text)
        skills_score, skills_details = self.calculate_skills_analysis_score(sections, processed_text)
        action_verbs_score, action_verbs_details = self.calculate_action_verbs_score(sections)
        presentation_score, presentation_details = self.calculate_professional_presentation_score(processed_text)
        industry_score, industry_details = self.calculate_industry_specific_score(sections, processed_text)
        
        # Calculate weighted overall score
        overall_score = (
            completeness_score * self.weights['content_completeness'] +
            quality_score * self.weights['content_quality'] +
            structure_score * self.weights['structure_formatting'] +
            skills_score * self.weights['skills_analysis'] +
            action_verbs_score * self.weights['action_verbs'] +
            presentation_score * self.weights['professional_presentation'] +
            industry_score * self.weights['industry_specific']
        )
        
        # Determine grade
        if overall_score >= 90:
            grade = 'A+'
            grade_description = 'Excellent'
        elif overall_score >= 80:
            grade = 'A'
            grade_description = 'Very Good'
        elif overall_score >= 70:
            grade = 'B+'
            grade_description = 'Good'
        elif overall_score >= 60:
            grade = 'B'
            grade_description = 'Above Average'
        elif overall_score >= 50:
            grade = 'C+'
            grade_description = 'Average'
        elif overall_score >= 40:
            grade = 'C'
            grade_description = 'Below Average'
        else:
            grade = 'D'
            grade_description = 'Needs Improvement'
        
        # Generate recommendations
        recommendations = self.generate_recommendations({
            'completeness': completeness_score,
            'quality': quality_score,
            'structure': structure_score,
            'skills': skills_score,
            'action_verbs': action_verbs_score,
            'presentation': presentation_score,
            'industry': industry_score
        })
        
        return {
            'overall_score': round(overall_score, 2),
            'grade': grade,
            'grade_description': grade_description,
            'component_scores': {
                'content_completeness': round(completeness_score, 2),
                'content_quality': round(quality_score, 2),
                'structure_formatting': round(structure_score, 2),
                'skills_analysis': round(skills_score, 2),
                'action_verbs': round(action_verbs_score, 2),
                'professional_presentation': round(presentation_score, 2),
                'industry_specific': round(industry_score, 2)
            },
            'detailed_analysis': {
                'completeness': completeness_details,
                'quality': quality_details,
                'structure': structure_details,
                'skills': skills_details,
                'action_verbs': action_verbs_details,
                'presentation': presentation_details,
                'industry': industry_details
            },
            'recommendations': recommendations,
            'sections_found': list(sections.keys())
        }
    
    def generate_recommendations(self, scores: Dict[str, float]) -> List[str]:
        """Generate specific recommendations based on scores"""
        recommendations = []
        
        if scores['completeness'] < 70:
            recommendations.append("Add missing essential sections like Contact Information, Summary, Experience, Education, and Skills")
        
        if scores['quality'] < 70:
            recommendations.append("Use more action verbs and quantifiable achievements in your experience descriptions")
            recommendations.append("Include specific metrics and results to demonstrate impact")
        
        if scores['structure'] < 70:
            recommendations.append("Improve formatting with consistent headers, bullet points, and proper spacing")
            recommendations.append("Ensure clear section organization and professional presentation")
        
        if scores['skills'] < 70:
            recommendations.append("Add more relevant technical and soft skills")
            recommendations.append("Categorize skills by type (Technical, Soft Skills, Tools, etc.)")
        
        if scores['action_verbs'] < 70:
            recommendations.append("Start bullet points with strong action verbs like 'Developed', 'Implemented', 'Led', 'Achieved'")
        
        if scores['presentation'] < 70:
            recommendations.append("Review grammar and spelling for professional presentation")
            recommendations.append("Use concise, clear language throughout the resume")
        
        if scores['industry'] < 70:
            recommendations.append("Add industry-specific keywords and relevant certifications")
            recommendations.append("Include projects and achievements specific to your target industry")
        
        if not recommendations:
            recommendations.append("Great job! Your resume is well-structured and comprehensive")
        
        return recommendations 