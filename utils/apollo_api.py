import requests
import json
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

API_CONFIG = {
    'client_id': '074c933c-112f-4acf-a6a5-3199e4c78eea',
    'client_secret': 'ff7c6a75-1336-4594-b74e-f26065b87d4e',
    'model_name': 'gpt-4.1',
    'token_url': 'https://api-gw.boehringer-ingelheim.com:443/api/oauth/token',
    'api_url': 'https://api-gw.boehringer-ingelheim.com:443/apollo/llm-api/',
    'temperature': 0.2,
    'max_tokens': 4000,
    'completions_path': 'chat/completions'
}

class ApolloAPIClient:
    def __init__(self):
        self.access_token = None
        self.config = API_CONFIG
    
    def get_access_token(self) -> Optional[str]:
        try:
            response = requests.post(
                self.config['token_url'],
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                data={
                    'grant_type': 'client_credentials',
                    'client_id': self.config['client_id'],
                    'client_secret': self.config['client_secret']
                },
                timeout=10
            )
            if response.status_code == 200:
                self.access_token = response.json().get('access_token')
                return self.access_token
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def call_llm(self, prompt: str, system_prompt: str = None, temperature: float = None, max_tokens: int = None) -> Optional[str]:
        if not self.access_token:
            if not self.get_access_token():
                return None
        
        try:
            messages = []
            if system_prompt:
                messages.append({'role': 'system', 'content': system_prompt})
            messages.append({'role': 'user', 'content': prompt})
            
            url = f"{self.config['api_url']}{self.config['completions_path']}"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': self.config['model_name'],
                'messages': messages,
                'temperature': temperature if temperature is not None else self.config['temperature'],
                'max_tokens': max_tokens if max_tokens is not None else self.config['max_tokens']
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=90)
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            elif response.status_code == 401:
                if self.get_access_token():
                    headers['Authorization'] = f'Bearer {self.access_token}'
                    response = requests.post(url, headers=headers, json=payload, timeout=90)
                    if response.status_code == 200:
                        return response.json()['choices'][0]['message']['content']
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def analyze_resume(self, resume_text: str, job_description: str) -> Optional[Dict]:
        system_prompt = """You are an expert HR analyst for Boehringer Ingelheim. Analyze resumes objectively."""

        user_prompt = f"""Analyze resume against job description.

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}

Provide JSON:
{{
  "candidate_name": "Full name",
  "email": "Email",
  "phone": "Phone",
  "years_experience": number,
  "technical_fit_score": 0-100,
  "technical_fit_justification": "Explanation with evidence",
  "behavioral_scores": {{
    "communicate_with_candor": {{"score": 1-5, "justification": "Evidence"}},
    "decide_and_act_with_speed": {{"score": 1-5, "justification": "Evidence"}},
    "innovate_and_drive_change": {{"score": 1-5, "justification": "Evidence"}},
    "deliver_to_win": {{"score": 1-5, "justification": "Evidence"}},
    "collaborate_with_a_purpose": {{"score": 1-5, "justification": "Evidence"}}
  }},
  "overall_recommendation": "SHORTLIST" or "MAYBE" or "REJECT",
  "recommendation_justification": "Summary",
  "key_strengths": ["strength1", "strength2", "strength3"],
  "key_concerns": ["concern1", "concern2"],
  "missing_requirements": ["req1", "req2"]
}}

SCORING: Tech>75 & Behavior>3.5 = SHORTLIST, Tech 60-75 = MAYBE, Tech<60 = REJECT
Return ONLY valid JSON."""

        response = self.call_llm(user_prompt, system_prompt, temperature=0.1, max_tokens=3000)
        
        if response:
            try:
                response = response.strip()
                if response.startswith('```json'):
                    response = response[7:]
                if response.startswith('```'):
                    response = response[3:]
                if response.endswith('```'):
                    response = response[:-3]
                return json.loads(response.strip())
            except:
                return None
        return None
    
    def analyze_resumes_parallel(self, resume_files: dict, job_description: str, batch_size: int = 2):
        """Analyze resumes in parallel batches"""
        def analyze_single(item):
            filename, resume_text = item
            result = self.analyze_resume(resume_text, job_description)
            if result:
                result['resume_filename'] = filename
                return result
            return {
                'resume_filename': filename,
                'candidate_name': filename.replace('Resume_', '').replace('.txt', '').replace('_', ' '),
                'error': 'Failed'
            }
        
        results = []
        items = list(resume_files.items())
        
        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            futures = [executor.submit(analyze_single, item) for item in items]
            for future in as_completed(futures):
                results.append(future.result())
        
        return results
    
    def generate_interview_questions(self, candidate_data: Dict, job_description: str) -> Optional[Dict]:
        system_prompt = """You are an expert interview coach."""
        
        user_prompt = f"""Generate interview questions for:

CANDIDATE:
Name: {candidate_data.get('candidate_name')}
Experience: {candidate_data.get('years_experience')} years
Technical Fit: {candidate_data.get('technical_fit_score')}/100
Strengths: {', '.join(candidate_data.get('key_strengths', []))}
Concerns: {', '.join(candidate_data.get('key_concerns', []))}

JOB: Senior Data Engineer

JSON format:
{{
  "technical_questions": [
    {{"question": "Question", "why_ask": "Reason", "good_answer": "Expected"}},
    ...5 questions
  ],
  "behavioral_questions": [
    {{"behavior": "Behavior name", "question": "Question", "why_ask": "Reason", "good_answer": "Expected"}},
    ...5 questions
  ],
  "case_study": {{
    "scenario": "Problem description",
    "what_to_assess": ["skill1", "skill2"],
    "evaluation_criteria": ["criterion1", "criterion2"]
  }}
}}

Return ONLY valid JSON."""

        response = self.call_llm(user_prompt, system_prompt, temperature=0.3, max_tokens=3000)
        
        if response:
            try:
                response = response.strip()
                if response.startswith('```json'):
                    response = response[7:]
                if response.startswith('```'):
                    response = response[3:]
                if response.endswith('```'):
                    response = response[:-3]
                return json.loads(response.strip())
            except:
                return None
        return None
