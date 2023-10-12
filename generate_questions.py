import json
import os
import re
import logging
import time
import requests
import sys
import argparse
import string

class TTService:
    def __init__(self, cfg) -> None:
        self.cfg = cfg
    
    def post_to_llm_eas(self, query_prompt):
        url = self.cfg['EASCfg']['url']
        author_key = self.cfg['EASCfg']['token']
        headers = {
            "Authorization": author_key,
            'Accept': "*/*",
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
        }
        resp = requests.post(
            url=url,
            data=query_prompt.encode('utf8'),
            headers=headers,
            timeout=None,
        )
        return resp.text

    def user_query(self, query):
        user_prompt_template = self.cfg['prompt_template'] + " " + query
        print("Post user query to TongYi QianWen")
        start_time = time.time()
        ans = self.post_to_llm_eas(user_prompt_template)
        end_time = time.time()
        print("Get response from EAS-Llama 2. Cost time: {} s".format(end_time - start_time))
        print(ans)
        return ans
    
def clean_questions(raw_questions):
    questions = raw_questions.split('?')
    # Initialize a list to store cleaned questions
    cleaned_questions = []

    # Define a regular expression pattern to match and remove question numbers
    question_number_pattern = re.compile(r'^\s*\d+[).]?\s*')

    # Iterate through each question and remove question numbers
    for question in questions:
        # Remove question numbers using regular expression substitution
        cleaned_question = question_number_pattern.sub('', question).strip()
        if len(question) > 0:
            cleaned_questions.append(cleaned_question + "?")
    cleaned_questions = '\n'.join(cleaned_questions)
    return [cleaned_questions , cleaned_questions]

def generate_question(query, config_dir='config.json'):
    if not os.path.exists(config_dir):
        print("Configuration file does not exist at relative path \"", config_dir, "\"")
    elif len(query) > 1700:
        print("Query exceeds maximum length 1700 characters.")
    else:
        with open(config_dir) as f:
            cfg = json.load(f)
            llm_service = TTService(cfg)
            if query.lower().translate(str.maketrans('', '', string.punctuation)) == "who are you":
                print("I am TalkTrainer. I'll be listening and paying attention to your presentation. You've got this!")
            else:
                answer = llm_service.user_query(query)
                return(clean_questions(answer))
                
# Example input for testing.
# print(generate_questions("Mohamed Bin Zayed University of Artificial Intelligence is a graduate-level, research-based academic institution located in Abu Dhabi, United Arab Emirates. The current president, Professor Eric Xing, joined in January 2021. The university offers graduate-level students a range of postgraduate degrees, focusing on core components of the AI industry: Computer Vision, Machine Learning, and Natural Language Processing. MBZUAI offers graduate-level degrees that are research-intensive and focused on practical AI. Hao Li is CEO and co-founder of Pinscreen, a startup that builds cutting edge AI-driven virtual avatar technologies, as well as associate professor at the Mohamed bin Zayed University of Artificial Intelligence (MBZUAI). He was previously a Distinguished Fellow of the Computer Vision Group at UC Berkeley and Associate Professor of Computer Science at the University of Southern California, where he was also director of the USC Institute for Creative Technologies. HAO LI, Associate Professor of Computer Vision at Abu Dhabi’s Mohamed bin Zayed University of Artificial Intelligence (MBZUAI), has been hard at work directing the Metaverse Lab. This new research center is at the heart of the university’s focus to integrate computer vision, graphics, and machine learning. Officially launched in 2015, Li’s AI startup, Pinscreen,is consistently giving rise to building digital humans for metaverse applications and visual effects. In fact, the company worked with Expo 2020 Dubai to generate millions of avatars for the six-month event's Xplorer application. With top minds alongside one another, the lab works on applied research to develop AI-powered immersive technologies."))

