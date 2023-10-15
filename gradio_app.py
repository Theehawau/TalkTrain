import os
import shutil
import numpy as np
import gradio as gr
import os.path as op
from llm_service import LLMService
from utils import *
from generate_questions import generate_question
from transformers import pipeline
import wave
from pydub import AudioSegment

WORK_DIR = os.getcwd()
SLIDES_PATH = WORK_DIR + "/slides/"
PANELS_PATH = WORK_DIR + "/results/"
placeholder = 'Your transcription appears here.'
questions = None
pipe = pipeline("automatic-speech-recognition", model="openai/whisper-tiny.en")
transcript = ""
chars_since_metric_update = 0
chars_since_question_gen = 0
QUESTION_UPDATE_INTERVAL = 500 # After how many characters spoken to auto-generate questions

def create_empty_wav():
    with wave.open("recording.wav", "w") as wav_file:
        wav_file.setnchannels(1)  # 1 for mono, 2 for stereo
        wav_file.setsampwidth(2)  # Sample width in bytes (2 for 16-bit PCM)
        wav_file.setnframes(0)  # Number of frames (set to 0 for an empty file)
        wav_file.setframerate(44100)  # Sample rate in Hz
        wav_file.setcomptype("NONE", "not compressed")  # Compression type and name

create_empty_wav()

def transcribe(audio, state=""):
    global transcript
    time.sleep(4)
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

def check_generate_questions(state, packet, current_questions):
    questions = current_questions
    global chars_since_question_gen
    if chars_since_question_gen >= QUESTION_UPDATE_INTERVAL:
        print("State has reached an interval of {QUESTION_UPDATE_INTERVAL} characters. Time to update metrics.")
        chars_since_question_gen = 0
        # print("Transcript hit {QUESTION_GENERATION_INTERVAL} characters without manual send. Sending generation request.")
        print(f'Transcript: {state[-QUESTION_UPDATE_INTERVAL:]}')
        questions = generate_question(state[-QUESTION_UPDATE_INTERVAL:], state="")
        generate_video(questions)
    chars_since_question_gen += len(packet)
    # print(questions)
    return questions


def check_update_metrics(state, packet, speech_rate, pause_rate, pitch_sd, feedback):
    print("State is: ", len(state), " characters long.")
    global chars_since_metric_update
    if chars_since_metric_update >= 400:
        chars_since_metric_update = 0
        print("State has reached an interval of 400 characters. Time to update metrics.")
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
    text_size='sm'
)

css = "footer {visibility: hidden}"

with gr.Blocks(title = 'TalkTrain', theme=theme, css=css) as demo:
    spoken_questions= gr.State(value=0)
    state = gr.State(value="")
    uploaded_slides_var = gr.State(value=[""])
    gr.Markdown("<div align='center'> <h2>  <span style='color:#FFA500;'> TalkTrain </span> : Your Pitching Assistant (GITEX x Alibaba Cloud Hackathon 2023) </h2> </div>")
    
    
    with gr.Tab("Simulate Q&A session!" ,id="qa"):
        gr.Markdown("Engage with questions from Panel regarding your presentation. You can upload your powerpoint exported as Images.")
        
        with gr.Row().style(equal_height=True):
            with gr.Column(scale=1) as panel:
                question_video = gr.Video('/home/kane/TalkTrain/Panel2.mp4', label='TalkTrainer', autoplay=True, height=400, width=400, show_download_button=False)
               
            with gr.Column(scale=2, visible = False) as slides:
                slide = gr.Image(type='filepath', show_label=False, size=(350,None), show_download_button=False)
                current_slide =gr.Number(value = 1, visible=False)
                with gr.Row():
                    prev = gr.Button("Previous")
                    next = gr.Button("Next")
            with gr.Column(scale=2) as upload_slides:
                slide_files = gr.File(label="Upload PPT as images",file_count='multiple', file_types=['image'], type='file', height=400)
        
        with gr.Row():
            mic_input = gr.Audio(source="microphone", label="Begin Presenting",type="filepath")
            any_question = gr.Button('Any Questions?', interactive=False, variant='primary', size='sm')


        with gr.Column() as comments:
            audio_output = gr.Textbox(label = "Your Speech, transcribed:")
            with gr.Row() as metrics:
                with gr.Row():
                    s_r = gr.Number(label="Speech Rate:", show_label=True, value=0.0, interactive=False, precision=2, min_width=100)
                    p_r =  gr.Number(label="Pause Rate:", show_label=True,value=0.0,interactive=False , precision=2, min_width=100 )
                    p_sd = gr.Number(label="Pitch SD:", show_label=True,value=0.0, interactive=False , precision=2, min_width=100)
                speech_metrics = gr.Textbox(label = "Comments on your speech metrics", placeholder="Comments on your speech appears here!", max_lines=3)
            questions_output_speech = gr.Textbox(label = "Questions for you:",  show_label=True, value=transcript)
    
    with gr.Tab("Transcription"):
        text_input = gr.Textbox(label="Type Speech:", show_label=True, autoscroll=True, max_lines=6) #, value=placeholder
        file_input = gr.File(label="Upload Transcription File", file_count='single', height=100)
        speech = gr.Text(label="My Speech:", show_label=True,  placeholder=placeholder, value=transcript)
        question_button1 = gr.Button("Any Questions?", interactive=False, variant='primary')
        questions_output_text = gr.Textbox(label="TalkTrain's Questions:", show_label=True, value=transcript)
    
    prev.click(sub,[uploaded_slides_var, current_slide],current_slide).then(previous, [current_slide], [slide], queue=False)
    
    next.click(add, [uploaded_slides_var,current_slide],current_slide).then(next_slide, [current_slide], [slide], queue=False)
    
    # for delay in case of upload cancel the lambda function
    slide_files.upload(Upload, [slide_files, uploaded_slides_var], [uploaded_slides_var], queue=False)\
        .then(lambda: time.sleep(2), outputs=None)\
        .then(slide_show,uploaded_slides_var  ,outputs=[slides,upload_slides, slide])

    slide_files.clear(Remove, uploaded_slides_var, uploaded_slides_var)

    mic_input.stream(fn=transcribe, inputs=[mic_input, state], outputs=[audio_output, state])
    
    mic_input.stream(fn=check_update_metrics, inputs=[state, mic_input, s_r, p_r, p_sd, speech_metrics], outputs=[s_r, p_r, p_sd, speech_metrics])
    mic_input.stream(fn=check_generate_questions, inputs=[state, mic_input, questions_output_speech], outputs=[questions_output_speech])

    any_question.click(make_question_video, [spoken_questions, questions_output_speech], [question_video, spoken_questions], queue=False)


    gr.on(
        questions_output_speech.change,
        activate_button,
        questions_output_speech,
        any_question
    )
        
    file_input.upload(use_file, file_input, speech)
    gr.on(
        triggers=[text_input.change, file_input.upload],
        fn = use_text,
        inputs=[text_input, file_input],
        outputs=speech
    ).then(activate_button, speech, question_button1)

   
    question_button1\
        .click(generate_question, inputs=[speech], outputs=[questions_output_text])
    
    

if __name__ == '__main__':
    shutil.rmtree(SLIDES_PATH)
    os.mkdir(SLIDES_PATH)
    shutil.rmtree(PANELS_PATH)
    os.mkdir(PANELS_PATH)
    demo.queue()
    demo.launch(share=True)
