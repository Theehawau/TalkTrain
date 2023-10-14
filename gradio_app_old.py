import numpy as np
import gradio as gr
from llm_service import LLMService
transcript = ""
from utils import *
from generate_questions import generate_question

placeholder = 'Your transcription appears here.'
questions = None

with gr.Blocks(title = 'TalkTrain') as demo:
   
    with gr.Tab("Transcription"):
        text_input = gr.Textbox(label="Type Speech:", show_label=True) #, value=placeholder
        file_input = gr.File(label="Upload Transcription File", file_count='single')
        speech = gr.Text(label="My Speech:", show_label=True,  placeholder=placeholder, value = transcript)
        question_button1 = gr.Button("Any Questions?", interactive=False)
        questions_output_text = gr.Textbox(label="TalkTrain's Questions:", show_label=True, value=transcript)
        
    
    with gr.Tab("Speech"):
        with gr.Row():
            mic_input = gr.Audio(source="microphone", type="filepath")
            recorded_input = gr.Audio(source="upload", type="filepath")
        audio_output = gr.Textbox(label="Your Transcribed Speech:", show_label=True, interactive=True, show_copy_button=True)
        
        with gr.Row():
            remarks_button = gr.Button("How's my speech?")
            question_button2 = gr.Button("Any Questions?")

        with gr.Column():
            with gr.Row() as metrics:
                s_r = gr.Number(label="Speech Rate:", show_label=True, value=0.0, interactive=False)
                p_r =  gr.Number(label="Pause Rate:", show_label=True,value=0.0,interactive=False  )
                p_sd = gr.Number(label="Pitch SD:", show_label=True,value=0.0, interactive=False )
            
            
            speech_metrics = gr.Textbox(label="TalkTrain's Comments On Your Speech:", show_label=True, placeholder="Comments on your speech appears here!")
            questions_output_speech = gr.Textbox(label="TalkTrain's Questions:", show_label=True, value=transcript)

    
    with gr.Tab("Simulate Q&A session!" ,id="qa"):
        gr.Markdown("Engage with questions from Panel regarding your presentation.")
        warning = gr.Markdown("First provide your presentation transcript or audio and generate questions.")
        
        countdown = gr.Button("Start Q&A session!", interactive=False)

        count = gr.Textbox(value="Starting CountDown", visible=False)

        with gr.Row(visible=False) as panel:
            gr.Video('2023_10_11_21.11.30.mp4', autoplay = False)
            gr.Image()
            # gr.Image()
            # gr.Image()
    
    gr.on(
        triggers=[text_input.change, file_input.upload],
        fn = use_text,
        inputs=[text_input, file_input],
        outputs=speech
    ).then(activate_button, speech, question_button1)

    gr.on(
        triggers=[mic_input.stop_recording, recorded_input.upload],
        fn = use_audio,
        inputs=[mic_input, recorded_input],
        outputs=audio_output
    )

    question_button1\
        .click(generate_question, inputs=speech, outputs=[questions_output_text, questions_output_speech])\
        .then(activate_interactive, None, outputs=[countdown, warning])
    question_button2.click(generate_question, inputs=audio_output, outputs=[questions_output_text, questions_output_speech]).then(activate_interactive, None, outputs=[countdown, warning])

    remarks_button.click(get_rate_metrics, [mic_input, recorded_input], [s_r, p_r, p_sd], queue = False).\
        then(analyze_speech_metrics, [s_r, p_r, p_sd], speech_metrics, queue = False)
    
    countdown.click(activate_count, None, count)\
        .then(count_down, countdown , count)\
        .then(activate_panel, questions_output_text, [panel, count, countdown])




if __name__ == '__main__':
    demo.queue()
    demo.launch()
