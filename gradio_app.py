import numpy as np
import gradio as gr
from llm_service import LLMService
from utils import *
from generate_questions import generate_question
from transformers import pipeline
import wave
from pydub import AudioSegment

placeholder = 'Your transcription appears here.'
questions = None
pipe = pipeline("automatic-speech-recognition", model="openai/whisper-tiny.en")
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

def check_generate_questions(state, packet, current_questions):
    questions = current_questions
    global chars_since_question_gen
    if chars_since_question_gen >= QUESTION_UPDATE_INTERVAL:
        chars_since_question_gen = 0
        print("Transcript hit {QUESTION_GENERATION_INTERVAL} characters without manual send. Sending generation request.")
        questions = generate_question(state[-QUESTION_UPDATE_INTERVAL:])
        generate_videos(questions)
    chars_since_question_gen += len(packet)
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


with gr.Blocks(title = 'TalkTrain') as demo:
   
    with gr.Tab("Transcription"):
        text_input = gr.Textbox(label="Type Speech:", show_label=True, autoscroll=True, max_lines=6) #, value=placeholder
        file_input = gr.File(label="Upload Transcription File", file_count='single')
        speech = gr.Text(label="My Speech:", show_label=True,  placeholder=placeholder, value=transcript)
        question_button1 = gr.Button("Any Questions?", interactive=False)
        questions_output_text = gr.Textbox(label="TalkTrain's Questions:", show_label=True, value=transcript)
        
    
    with gr.Tab("Speech"):
        
        state = gr.State(value="")

        with gr.Row():
            audio_output = gr.Textbox(label="Your Transcribed Speech:", show_label=True, interactive=True, show_copy_button=True, value = transcript)

        with gr.Row():
            with gr.Column():
                mic_input = gr.Audio(source="microphone", type="filepath")
            with gr.Column():
                recorded_input = gr.Audio(source="upload", type="filepath")

        mic_input.stream(fn=transcribe, inputs=[mic_input, state], outputs=[audio_output, state])
        
        
        
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
            
        mic_input.stream(fn=check_update_metrics, inputs=[state, mic_input, s_r, p_r, p_sd, speech_metrics], outputs=[s_r, p_r, p_sd, speech_metrics])
        mic_input.stream(fn=check_generate_questions, inputs=[state, mic_input, questions_output_speech], outputs=[questions_output_speech])
        
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

    remarks_button.click(get_rate_metrics, [state, recorded_input], [s_r, p_r, p_sd], queue = False).\
        then(analyze_speech_metrics, [s_r, p_r, p_sd], speech_metrics, queue = False)
    
    countdown.click(activate_count, None, count)\
        .then(count_down, countdown , count)\
        .then(activate_panel, questions_output_text, [panel, count, countdown])


if __name__ == '__main__':
    demo.queue()
    demo.launch()
