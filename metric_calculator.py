from voicelab.src.Voicelab.toolkits.Voicelab.MeasureSpeechRateNode import MeasureSpeechRateNode
from voicelab.src.Voicelab.toolkits.Voicelab.MeasurePitchNode import MeasurePitchNode
import parselmouth
import os

AUDIO_DIR = "audio_files"

def prepare_nodes(file_name):
    # Load the sound using parselmouth and set up node
    file_path = os.path.join(AUDIO_DIR, file_name)
    rate_node = MeasureSpeechRateNode()
    pitch_node = MeasurePitchNode()

    rate_node.args["file_path"] = pitch_node.args["file_path"] = file_path
    
    try:
        sound: parselmouth.Sound = parselmouth.Sound(file_path)
        signal = sound.values
        sampling_rate = sound.sampling_frequency
    except:
        signal = None
        sampling_rate = None

    rate_node.voice = pitch_node.voice = (signal, sampling_rate)
    rate_node.args["voice"] = pitch_node.args["voice"] = signal, sampling_rate
    print((f"{file_path=}..{sampling_rate=}"))
    return rate_node, pitch_node


def get_rate_metrics(test_file):
    rate_node, pitch_node = prepare_nodes(test_file)
    rate_metrics = rate_node.process()
    pitch_metrics = pitch_node.process()
    speech_rate = rate_metrics['speechrate(Number of Syllables / Duration)']
    speech_duration = rate_metrics['Duratrion(s)']
    num_pauses = rate_metrics['Number of Pauses']
    pause_rate = num_pauses / speech_duration
    pitch_sd = pitch_metrics['Standard Deviation Pitch (F0) (Praat To Pitch (ac))']

    return speech_rate, pause_rate, pitch_sd

speech_rate, pause_rate, pitch_sd = get_rate_metrics('metaverse_article_recording_half.wav')

print("Speech Rate:", speech_rate)
if speech_rate < 3.0:
    print("Speech rate is low. Try to speak at a faster pace.")
elif speech_rate > 5.0:
    print("Speech rate is high. Try to speak more slowly.")
else:
    print("Your speech rate is good. Keep it up!")

print("Pause Rate:", pause_rate)
if pause_rate < 0.2:
    print("Pause rate is low. Take a breath!")
elif pause_rate > 0.4:
    print("Pause rate is high. Try to speak more fluently.")
else:
    print("Your pause rate is good. Keep it up!")

print("Standard Deviation of Pitch:", pitch_sd)
if pitch_sd < 15:
    print("Pitch variation is low. Your speech may sound monotone.")
elif pitch_sd > 32:
    print("Pitch variation is high. Try to speak in a more consistent tone.")
else:
    print("Your pitch variation is good. Keep it up!")

# Filler word count metric must be calculated from trascript, not .wav
