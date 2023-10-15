import os
import time
import wave
import random
import shutil
import numpy as np
import gradio as gr
import os.path as op
from utils import *
from pydub import AudioSegment
from transformers import pipeline
from generate_questions import generate_question



WORK_DIR = os.getcwd()
SLIDES_PATH = WORK_DIR + "/slides/"
PANELS_PATH = WORK_DIR + "/results/"
pipe = pipeline("automatic-speech-recognition", model ="openai/whisper-tiny.en")
transcript = ""
chars_since_metric_update = 0
chars_since_question_gen = 0
QUESTION_UPDATE_INTERVAL = 200 # After how many characters spoken to auto-generate questions

def create_empty_wav():
    with wave.open("recording.wav", "w") as wav_file:
        wav_file.setnchannels(1)  # 1 for mono, 2 for stereo
        wav_file.setsampwidth(2)  # Sample width in bytes (2 for 16-bit PCM)
        wav_file.setnframes(0)  # Number of frames (set to 0 for an empty file)
        wav_file.setframerate(44100)  # Sample rate in Hz
        wav_file.setcomptype("NONE", "not compressed")  # Compression type and name

create_empty_wav()

def check_generate_questions(state, packet, current_questions):
    questions = current_questions
    global chars_since_question_gen
    if chars_since_question_gen >= QUESTION_UPDATE_INTERVAL and len(state[-QUESTION_UPDATE_INTERVAL:]) > 150:
        print("State has reached an interval of {QUESTION_UPDATE_INTERVAL} characters. Time to update metrics.")
        chars_since_question_gen = 0
        print("Transcript hit {QUESTION_GENERATION_INTERVAL} characters without manual send. Sending generation request.")
        questions = generate_question(state[-QUESTION_UPDATE_INTERVAL:], state="REAL")
        generate_videos(questions)
    chars_since_question_gen += len(packet)
    # print(questions)
    return questions

def check_update_metrics(state, packet, speech_rate, pause_rate, pitch_sd, feedback):
    print("State is: ", len(state), " characters long.")
    global chars_since_metric_update
    if chars_since_metric_update >= 200:
        chars_since_metric_update = 0
        print("State has reached an interval of 200 characters. Time to update metrics.")
        recording = AudioSegment.from_wav("recording.wav")
        last_10_seconds = recording[-10000:]
        last_10_seconds.export("last_10_seconds.wav", format="wav")
        speech_rate, pause_rate, pitch_sd = get_rate_metrics("last_10_seconds.wav", None)
        feedback = analyze_speech_metrics(speech_rate, pause_rate, pitch_sd)
    chars_since_metric_update += len(packet)
    return speech_rate, pause_rate, pitch_sd, feedback

theme = gr.themes.Soft(
    primary_hue="orange",
    secondary_hue="blue",
    neutral_hue="stone",
    font=[gr.themes.GoogleFont('Comfortaa'), 'ui-sans-serif', 'system-ui', 'sans-serif'],
)


with gr.Blocks(title = 'TalkTrain', theme=theme) as demo:
    spoken_questions= gr.State(value=0)
    state = gr.State(value="")
    uploaded_slides_var = gr.State(value=[""])
    gr.Markdown("<div align='center'> <h2> TalkTrain: Your Pitch Audience (GITEX x AliBaba Cloud Hackathon 2023) </span> </h2> \
                    <a style='font-size:18px;color: #EFEFEF' href='https://arxiv.org/abs/2211.12194'>Arxiv</a> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; \
                    <a style='font-size:18px;color: #EFEFEF' href='https://sadtalker.github.io'>Homepage</a>  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; \
                     <a style='font-size:18px;color: #EFEFEF' href='https://github.com/Theehawau/TalkTrain'> Github </div>")
    with gr.Row().style(equal_height=True, height=350):
        with gr.Column(scale=1) as panel:
            # gr.Markdown("Panel")
            question_video = gr.Video()
        with gr.Column(scale=2, visible = False) as slides:
            slide = gr.Image(type='filepath')
            current_slide =gr.Number(value = 1, visible=False)
            with gr.Row():
                prev = gr.Button("Previous")
                next = gr.Button("Next")
        with gr.Column() as upload_slides:
            slide_files = gr.File(label="Upload PPT as images",file_count='multiple', file_types=['image'], type='file')
    
    with gr.Row():
        mic_input = gr.Audio(source="microphone", label="Begin Presenting",type="filepath")
        any_question = gr.Button('Any Questions?')

    with gr.Column() as comments:
        audio_output = gr.Textbox(label = "Your Speech, transcribed:")
        with gr.Row() as metrics:
            s_r = gr.Number(label="Speech Rate:", show_label=True, value=0.0, interactive=False)
            p_r =  gr.Number(label="Pause Rate:", show_label=True,value=0.0,interactive=False  )
            p_sd = gr.Number(label="Pitch SD:", show_label=True,value=0.0, interactive=False )
        speech_metrics = gr.Textbox(label = "Comments on your speech metrics", placeholder="Comments on your speech appears here!")
        questions_output_speech = gr.Textbox(label = "Questions for you:",  show_label=True, value=transcript)
    
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
        return {uploaded_slides_var : uploaded_slides}
    
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
    
    prev.click(sub,[uploaded_slides_var, current_slide],current_slide).then(previous, [current_slide], [slide], queue=False)
    
    next.click(add, [uploaded_slides_var,current_slide],current_slide).then(next_slide, [current_slide], [slide], queue=False)
    
    # for delay in case of upload cancel the lambda function
    slide_files.upload(Upload, [slide_files, uploaded_slides_var], [uploaded_slides_var], queue=False)\
        .then(lambda: time.sleep(5), outputs=None)\
        .then(slide_show,uploaded_slides_var  ,outputs=[slides,upload_slides, slide])

    slide_files.clear(Remove, uploaded_slides_var, uploaded_slides_var)

    mic_input.stream(fn=transcribe, inputs=[mic_input, state], outputs=[audio_output, state])
    
    mic_input.stream(fn=check_update_metrics, inputs=[state, mic_input, s_r, p_r, p_sd, speech_metrics], outputs=[s_r, p_r, p_sd, speech_metrics])
    mic_input.stream(fn=check_generate_questions, inputs=[state, mic_input, questions_output_speech], outputs=[questions_output_speech])

    any_question.click(make_question_video, [spoken_questions, questions_output_speech], [question_video, spoken_questions])

if __name__=='__main__':
    shutil.rmtree(SLIDES_PATH)
    os.mkdir(SLIDES_PATH)
    shutil.rmtree(PANELS_PATH)
    os.mkdir(PANELS_PATH)
    demo.queue()
    demo.launch(debug = True)
