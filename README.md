## TalkTrain

TalkTrain is an AI-powered public speaking and presentation practise application.
Make your speech to our virtual assistant, and you will be provided with useful metrics, as well as questions extrapolated from your own presentation.

TalkTrain is an entry for the GITEX AI InnovateFest 2023 Hackathon, powered by Alibaba Cloud.

# Environment

We have tested TalkTrain in Ubuntu 20.04, from a conda environment.

# Install Instructions

1) git clone this repository

```bash
git clone https://github.com/Theehawau/TalkTrain.git
cd TalkTrain
```

2) Install the necessary packages onto your machine with apt install or similar.
    portaudio19-dev
    python3-all-dev

2) Create an environment with Python 3.10
```bash
conda create -n TalkTrain python=3.10
```

3) In the environment, install packages in requirements.txt using pip.

```bash 
conda activate TalkTrain
pip install -r requirements.txt
```

4) Please download the SadTalker weights from this Google drive for Face Animation(FA):
    https://drive.google.com/drive/folders/1UZxnS41k7QuseRqANcStSFKNXamUNtT_?usp=drive_link
    and place the folders in [SadTalker](../main/SadTalker/).

5) Setup Alibaba cloud services:
    - [LLM]()
    - [Intelligent Spech Services](https://www.alibabacloud.com/help/en/intelligent-speech-interaction/latest/activate-service#topic-2572187)

If you have ubuntu OS:

You can install all requirements with
```bash
bash install.sh
```

# Running Instructions


###  WebUI demo
```bash
conda activate TalkTrain
cd TalkTrain
gradio gradio_app.py
```

### Test Pipeline

You can run the file ``` bash python llm+tts+avatar_example.py ``` for testing the QG -> TTS -> FA pipeline.


# Issues, Limitations

You need an Alibaba cloud account and services initiated to test this out. A recorded demo is here
If you run into QS error 
```bash export QT_QPA_PLATFORM=offscreen ``` , setting this environment variable solves this.



# Acknowledgements

TalkTrain builds on existing technologies.

- Question Generation(QG): <a href=''> AliBaba TongChen LLM </a> 
- Automatic Speech Recognition (ASR): <a href=''> OpenAI whisper </a>   
- TTS: <a href='https://www.alibabacloud.com/help/en/intelligent-speech-interaction/latest/activate-service#topic-2572187'> Alibaba Intelligent Speech Interaction </a>  
- Avatar Animation: <a href='https://github.com/OpenTalker/SadTalker'> SadTalker </a>  

