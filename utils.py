import os
import time
import shutil
import os.path as op
import gradio as gr
import parselmouth
import speech_recognition as sr
import random

from tts import tts
from gtts import gTTS
from pydub import AudioSegment
from transformers import pipeline
from SadTalker.inference import get_avatar_video

pipe = pipeline("automatic-speech-recognition", model="openai/whisper-tiny.en")

from voicelab.src.Voicelab.toolkits.Voicelab.MeasureSpeechRateNode import MeasureSpeechRateNode
from voicelab.src.Voicelab.toolkits.Voicelab.MeasurePitchNode import MeasurePitchNode

r=sr.Recognizer()
rate_node = MeasureSpeechRateNode()
pitch_node = MeasurePitchNode()

WORK_DIR = os.getcwd()
SLIDES_PATH = WORK_DIR + "/slides/"
PANELS_PATH = WORK_DIR + "/results/"
AUDIO_DIR = WORK_DIR + '/audios/'
VIDEO_DIR = WORK_DIR + '/results/'
IMAGE_PATH = '/home/kane/TalkTrain/portraits/Panel2.png'


counter = 0

def generate_video(questions):
    global counter
    print('generation video called')
    if type(questions) == str:
        counter+=1
        split_questions = questions.split('\n')
        question_choice = random.randint(0, len(split_questions)-1)
        print(split_questions[question_choice])
        avatar_pipeline(split_questions[question_choice],counter)
    else:
        counter+=1
        question_choice = random.randint(0, len(questions)-1)
        print(questions[question_choice])
        avatar_pipeline(questions[question_choice],counter)
    return None

def avatar_pipeline(question, count):
    print(f'Generating video for {question}')
    tts('zE6Ckn248eJtl6Cd', '3914319793ba4bce8ef86cf326eb173e',question, f'{AUDIO_DIR}/Audio{count}.wav')
    # tts = gTTS(question)
    # tts.save(f'{AUDIO_DIR}/Audio{count}.wav')
    get_avatar_video(f'{AUDIO_DIR}/Audio{count}.wav',IMAGE_PATH, f'Panel{count}')
    return('Done!')

def generate_speech(text):
    return f"Input: \n {text}"

def generate_remarks(text):
    return f"Remarks: \n {text}"

def activate_interactive():
    return gr.Button(interactive=True), gr.Markdown(visible=False)

def activate_panel(text):
    print(text)
    return gr.Row(visible=True), gr.Textbox(visible = False), gr.Button(interactive=False)

def count_down(_, progress = gr.Progress(track_tqdm=True)):
    time.sleep(2)
    loop = [None] * 5
    for i in progress.tqdm(loop, desc = "Starting Q&A session"):
        time.sleep(2)
    return "Panels are ready!"

def activate_count():
    return gr.Textbox(value="Starting CountDown", show_label=False , visible=True)

def activate_button(text):
    if len(text) == 0:
        return gr.Button("Any Questions?", interactive=False)
    else:
        return gr.Button("Any Questions?", interactive=True)

def use_text(text, file):
    global transcript
    if text:
        transcript = text
        return f"{text}"
    elif file:
        return save_file(file)

def use_file(file):
    return save_file(file)

def save_file(file):
    global transcript
    with open(file.name, 'r') as f:
        transcript = f.read()
        return transcript
     
def use_audio(mic, recorded):
    global audio_path 
    if mic:
        audio_path = gr.Audio(mic, visible = False)
        with sr.AudioFile(mic) as source:
            audio = r.record(source)
    else:
        audio_path = gr.Audio(recorded, visible = False)
        with sr.AudioFile(recorded) as source:
            audio = r.record(source)
    global transcript
    transcript = r.recognize_google(audio, language='en-in')
    return transcript

def get_rate_metrics(mic, recorded):
    print('function called')
    test_file = mic if mic else recorded
    # rate_node, pitch_node = prepare_nodes(test_file)
    rate_node.args["file_path"] = pitch_node.args["file_path"] = test_file
    # Load the sound using parselmouth and set up node
    try:
        sound: parselmouth.Sound = parselmouth.Sound(test_file)
        signal = sound.values
        sampling_rate = sound.sampling_frequency
    except:
        signal = None
        sampling_rate = None

    rate_node.voice = pitch_node.voice = (signal, sampling_rate)
    rate_node.args["voice"] = pitch_node.args["voice"] = signal, sampling_rate
    rate_metrics = rate_node.process()
    pitch_metrics = pitch_node.process()
    speech_rate = rate_metrics['speechrate(Number of Syllables / Duration)']
    pause_rate = rate_metrics['Number of Pauses'] / rate_metrics['Duratrion(s)']
    pitch_sd = pitch_metrics['Standard Deviation Pitch (F0) (Praat To Pitch (ac))']
    print(f"{test_file=}..{sampling_rate=}")
    return speech_rate, pause_rate, pitch_sd

def analyze_speech_metrics(speech_rate, pause_rate, pitch_sd):
    sr =  analyze_rate("Speech rate", float(speech_rate), 3.0, 5.0)
    pr =  analyze_rate("Pause Rate", float(pause_rate), 0.2, 0.4)
    p_sd =  analyze_rate("Standard Deviation of Pitch", float(pitch_sd), 15, 32)

    return f"{sr}\n{pr}\n{p_sd}"

def analyze_rate(metric_name, value, lower_threshold, upper_threshold):
    response = ""
    # response += f"{metric_name}: {value}"
    if value < lower_threshold:
        response +=  f"Your {metric_name.lower()} is low. {get_recommendation(metric_name, 'faster')}"
    elif value > upper_threshold:
        response +=  f"Your {metric_name.lower()} is high. {get_recommendation(metric_name, 'slower')}"
    else:
        response +=  f"Your {metric_name.lower()} is good. Keep it up!"
    return response

def get_recommendation(metric_name, suggestion):
    if suggestion == 'faster':
        if metric_name == 'Speech rate':
            return f"Try to speak at a faster pace."
        elif metric_name == 'Pause Rate':
            return f'Take a breath!'
        elif metric_name == 'Standard Deviation of Pitch':
            return f'Your speech may sound monotone.'
        
    elif suggestion == 'slower':
        if metric_name == 'Speech rate':
            return f" Try to speak more slowly."
        elif metric_name == 'Pause Rate':
            return f' Try to speak more fluently.'
        elif metric_name == 'Standard Deviation of Pitch':
            return f'Try to speak in a more consistent tone.'
        

def previous(slide_no):
        file = f"{SLIDES_PATH}Slide{int(slide_no)}.PNG"
        return gr.Image(value = file, type='filepath')
    
def next_slide(slide_no):
    file = f"{SLIDES_PATH}Slide{int(slide_no)}.PNG"
    return gr.Image(value = file, type='filepath')

def add(uploaded_slides, x):
    max = len(uploaded_slides) - 1
    if x == max:
        return x
    return x+1

def sub(uploaded_slides, x):
    if x == 1:
        return x
    else:
        return x-1

def Upload(files, uploaded_slides):
    save_files = []
    for file in files:
        save_file = SLIDES_PATH + op.basename(file.name)
        shutil.copy(file.name, save_file)
        save_files.append(save_file)
    uploaded_slides.extend(save_files)
    return  uploaded_slides

def Remove(uploaded_slides):
    for file in uploaded_slides:
        if op.exists(file):os.remove(file)
    return gr.State(value=[""])

def slide_show(x):
    return gr.Column(visible=True), gr.Column(visible=False), gr.Image(value=x[1])

def transcribe(audio, state=""):
    global transcript
    time.sleep(4)
    print(audio)

    # Load the WAV files
    audio1 = AudioSegment.from_file("recording.wav", format="wav")
    audio2 = AudioSegment.from_file(audio, format="wav")
    # Concatenate the audio segments
    result = audio1 + audio2

    # Export the concatenated audio as a new WAV file
    result.export("recording.wav", format="wav")

    # Get rid of the glitch where silence generates the word "you".
    text = pipe(audio)["text"]
    if text.replace(" ", "") != "you":
        state += text + " "

    transcript = 'transciption'
    return state, state

def make_question_video(counter,questions):
    q = counter
    counter += 1
    return gr.Video(value = PANELS_PATH + f"Panel{q+1}.mp4", autoplay = True), counter
    