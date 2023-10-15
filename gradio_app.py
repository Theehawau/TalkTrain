import os
import wave
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
AUDIO_PATH = WORK_DIR + "/audios/"
placeholder = 'Your transcription appears here.'
questions = None
transcript = ""


def create_empty_wav():
    with wave.open("recording.wav", "w") as wav_file:
        wav_file.setnchannels(1)  # 1 for mono, 2 for stereo
        wav_file.setsampwidth(2)  # Sample width in bytes (2 for 16-bit PCM)
        wav_file.setnframes(0)  # Number of frames (set to 0 for an empty file)
        wav_file.setframerate(44100)  # Sample rate in Hz
        wav_file.setcomptype("NONE", "not compressed")  # Compression type and name

create_empty_wav()


# for webapp demo theme
theme = gr.themes.Soft(
    primary_hue="orange",
    secondary_hue="blue",
    neutral_hue="stone",
    font=[gr.themes.GoogleFont('Comfortaa'), 'ui-sans-serif', 'system-ui', 'sans-serif'],
    text_size='sm'
)
# remove footer
css = "footer {visibility: hidden}"

with gr.Blocks(title = 'TalkTrain', theme=theme, css=css) as demo:
    # state variables for keeping track of slides, quesstions etc.
    spoken_questions= gr.State(value=0)
    state = gr.State(value="")
    uploaded_slides_var = gr.State(value=[""])

    gr.Markdown("<div align='center'> <h2>  <span style='color:#FFA500;'> TalkTrain </span> : Your Pitching Assistant (GITEX x Alibaba Cloud Hackathon 2023) </h2> </div>")
    
    # Q & A simulation Tab
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
    
    # Transcription tab for uploading transcription file or typing in text
    with gr.Tab("Transcription"):
        text_input = gr.Textbox(label="Type Speech:", show_label=True, autoscroll=True, max_lines=6) #, value=placeholder
        file_input = gr.File(label="Upload Transcription File", file_count='single', height=100)
        speech = gr.Text(label="My Speech:", show_label=True,  placeholder=placeholder, value=transcript)
        question_button1 = gr.Button("Any Questions?", interactive=False, variant='primary')
        questions_output_text = gr.Textbox(label="TalkTrain's Questions:", show_label=True, value=transcript)
    
    # Presentation chane slide buttons
    prev.click(sub,[uploaded_slides_var, current_slide],current_slide).then(previous, [current_slide], [slide], queue=False)
    
    next.click(add, [uploaded_slides_var,current_slide],current_slide).then(next_slide, [current_slide], [slide], queue=False)
    
    # for delay in case of upload cancel the lambda function
    slide_files.upload(Upload, [slide_files, uploaded_slides_var], [uploaded_slides_var], queue=False)\
        .then(lambda: time.sleep(2), outputs=None)\
        .then(slide_show,uploaded_slides_var  ,outputs=[slides,upload_slides, slide])

    slide_files.clear(Remove, uploaded_slides_var, uploaded_slides_var)

    # Presentation streaming event listeners
    mic_input.stream(fn=transcribe, inputs=[mic_input, state], outputs=[audio_output, state])
    
    mic_input.stream(fn=check_update_metrics, inputs=[state, mic_input, s_r, p_r, p_sd, speech_metrics], outputs=[s_r, p_r, p_sd, speech_metrics])
    mic_input.stream(fn=check_generate_questions, inputs=[state, mic_input, questions_output_speech], outputs=[questions_output_speech])

    mic_input.stop_recording(stop_recording, state, state)

    # question button event listener for Q & A Tab
    any_question.click(make_question_video, [spoken_questions, questions_output_speech], [question_video, spoken_questions], queue=False)


    gr.on(
        questions_output_speech.change,
        activate_button,
        questions_output_speech,
        any_question
    )

    # transcript file upload event listener 
    file_input.upload(use_file, file_input, speech).then(activate_button, speech, question_button1)
    
    # text input event listener
    gr.on(
        triggers=[text_input.change],
        fn = use_text,
        inputs=[text_input],
        outputs=speech
    ).then(activate_button, speech, question_button1)

#    any questions event listener for transcription Tab
    question_button1\
        .click(generate_question, inputs=[speech], outputs=[questions_output_text])
    
    

if __name__ == '__main__':
    for folder in [SLIDES_PATH, PANELS_PATH, AUDIO_PATH]:
        if not op.exists(folder):
            os.makedir(folder)
        else:
            shutil.rmtree(folder)
            os.makedir(folder)
    demo.queue() #queuing event listeners to run in order, we set queue=False for the ones we want to run immediately
    demo.launch()
