from voicelab.src.Voicelab.toolkits.Voicelab.ReverseSoundsNode import ReverseSoundsNode
import parselmouth
import os
import numpy as np
from scipy.io import wavfile

AUDIO_DIR = "audio_files"

def get_test_files():
  number_of_test_files = len(os.listdir(AUDIO_DIR))
  test_files = sorted(os.listdir(AUDIO_DIR))
  return number_of_test_files, test_files

# Arrange
def prepare_node(test_file):
  file_path = os.path.join(AUDIO_DIR, test_file)
  node = ReverseSoundsNode()
  node.args['file_path'] = file_path
  # Load the sound and setup the node
  try:
      sound: parselmouth.Sound = parselmouth.Sound(file_path)
      signal = sound.values
      sampling_rate = sound.sampling_frequency
  except:
      signal = None
      sampling_rate = None
  node.voice = (signal, sampling_rate)
  node.args['voice'] = (signal, sampling_rate)
  print((f"{file_path=}..{sampling_rate=}"))
  return node

# Arrange
def get_reversed_test_sound(test_file):
  file_path = os.path.join(AUDIO_DIR, test_file)
  validation_sound = parselmouth.Sound(file_path)
  validation_sound.reverse()
  return validation_sound

output_file = "audio_files_output/output.wav"
num_files, test_files = get_test_files()
reversed_sound = get_reversed_test_sound(test_files[0])
print("Reversed Sound: ", reversed_sound)
print(type(reversed_sound))
reversed_sound.save(output_file, format="WAV")
