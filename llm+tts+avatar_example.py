from SadTalker.inference import get_avatar_video
from tts import tts
from generate_questions import generate_questions

if __name__ == "__main__":
    image_dir = 'SadTalker/guy3.png'
    audio_dir = 'syAudio.wav'
    transcript = r"Mohamed Bin Zayed University of Artificial Intelligence is a graduate-level, research-based academic institution located in Abu Dhabi, United Arab Emirates. The current president, Professor Eric Xing, joined in January 2021. The university offers graduate-level students a range of postgraduate degrees, focusing on core components of the AI industry: Computer Vision, Machine Learning, and Natural Language Processing. MBZUAI offers graduate-level degrees that are research-intensive and focused on practical AI. Hao Li is CEO and co-founder of Pinscreen, a startup that builds cutting edge AI-driven virtual avatar technologies, as well as associate professor at the Mohamed bin Zayed University of Artificial Intelligence (MBZUAI). He was previously a Distinguished Fellow of the Computer Vision Group at UC Berkeley and Associate Professor of Computer Science at the University of Southern California, where he was also director of the USC Institute for Creative Technologies. HAO LI, Associate Professor of Computer Vision at Abu Dhabi’s Mohamed bin Zayed University of Artificial Intelligence (MBZUAI), has been hard at work directing the Metaverse Lab. This new research center is at the heart of the university’s focus to integrate computer vision, graphics, and machine learning. Officially launched in 2015, Li’s AI startup, Pinscreen,is consistently giving rise to building digital humans for metaverse applications and visual effects. In fact, the company worked with Expo 2020 Dubai to generate millions of avatars for the six-month event's Xplorer application. With top minds alongside one another, the lab works on applied research to develop AI-powered immersive technologies."
    questions = generate_questions(transcript)
    tts('zE6Ckn248eJtl6Cd', 'dccf69c25151444a9d1a2a65a7cb6404', questions[0])
    get_avatar_video(audio_dir, image_dir)