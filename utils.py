import os
import time
import gradio as gr
import parselmouth
import speech_recognition as sr

from concurrent.futures import ProcessPoolExecutor

ppe = ProcessPoolExecutor()

from voicelab.src.Voicelab.toolkits.Voicelab.MeasureSpeechRateNode import MeasureSpeechRateNode
from voicelab.src.Voicelab.toolkits.Voicelab.MeasurePitchNode import MeasurePitchNode

r=sr.Recognizer()
rate_node = MeasureSpeechRateNode()
pitch_node = MeasurePitchNode()

# def generate_question(text):
#     print('genQ called')
#     global questions
#     questions = "questions available now"
#     return f"Input: \n {text}", f"Input: \n {text}"


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
        response +=  f"Your {metric_name.lower()} is low. {get_recommendation(metric_name, 'faster' if metric_name == 'Speech rate' else 'more fluently')}"
    elif value > upper_threshold:
        response +=  f"Your {metric_name.lower()} is high. {get_recommendation(metric_name, 'slower' if metric_name == 'Speech rate' else 'in a more consistent tone')}"
    else:
        response +=  f"Your {metric_name.lower()} is good. Keep it up!"
    return response

def get_recommendation(metric_name, suggestion):
    if metric_name == 'Speech rate':
        return f"Try to speak at a {suggestion} pace."
    else:
        return f"Try to speak {suggestion}."