
<div align="center">
<h2> <strong> TalkTrain </strong> </h2>

<a href=''><img src='https://img.shields.io/badge/Alibaba%20Cloud%20-orange'></a> &nbsp; <a href='https://youtu.be/Na4XdjN_FaM?si=9K7TArx8PfI4t0jw'><img src='https://img.shields.io/badge/demo-YouTube-red'></a> &nbsp;  <a href=''><img src='https://img.shields.io/badge/GITEX%20-orange'></a> &nbsp;

<div>
    <a href='https://www.linkedin.com/in/toyinhawau/' target='_blank'>Hawau Olamide Toyin <sup>1,2,3</sup> </a>&emsp;
    <a href='https://www.linkedin.com/in/kanelindsay1/' target='_blank'>Kane Lindsay<sup>1,2</a>&emsp;
</div>
<br>
<div>
    <sup>1</sup> MBZUAI &emsp; <sup>2</sup> Metaverse Lab, MBZUAI &emsp; <sup>3</sup> Speech Lab, MBZUAI &emsp; 
</div>
<br>
<i><strong><a href='https://middle-east.alibabacloud.com/campaign/ai_hackathon#J_9912546380' target='_blank'>GITEX AI InnovateFest 2023 Powered by Alibaba Cloud</a></strong></i>
<br>
<br>
</div>




TalkTrain is an AI-powered public speaking and presentation practise application.
Make your speech to our virtual assistant, and you will be provided with useful metrics, as well as questions extrapolated from your own presentation.

TalkTrain is an entry for the GITEX AI InnovateFest 2023 Hackathon, powered by Alibaba Cloud. Watch project presentation on [YouTube](https://youtu.be/Na4XdjN_FaM?si=9K7TArx8PfI4t0jw).

<h3>  (Coming SOON!!!) A step-by-step guide to build TalkTrain from scratch using Alibaba Cloud services </h3>

## Features

- [gradio_app.py](../master/gradio_app.py) - WebUI interface code and entry point
- [utils.py](../master/utils.py) - Helper functions for webUI event listeners, speech metrics calculation and Automatic-Speech-Recognition (ASR)
- [config.json](../master/config.json) - Configuration for tokens, prompts etc
- [tts.py](../master/tts.py) - Helper functions for Text-To-Speech (TTS)
- [generate_questions.py](../master/generate_questions.py) - Helper functions for Question-Generation (QG)
- [/SadTalker/inference.py](../master/SadTalker/inference.py) - Helper function for Face Animation (FA)

## Environment

We developed TalkTrain in Ubuntu 20.04 OS with python version 3.10

## Install Instructions

1) Clone this repository

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
    and place the folders in [SadTalker](../master/SadTalker/).

5) Setup Alibaba cloud services and configure tokens in [config](../master/config.json) and [utils](../master/utils.py) files:
    - [Tongyi Qianwen LLM](https://www.alibabacloud.com/blog/alibaba-integrates-llm-tongyi-qianwen-into-taobao-to-refine-e-commerce-searches-for-users_600401)
    - [Intelligent Spech Services](https://www.alibabacloud.com/help/en/intelligent-speech-interaction/latest/activate-service#topic-2572187)

If you have ubuntu OS:

You can install all requirements with 
```bash 
bash install.sh 
```


## Running Instructions


####  WebUI demo
```bash
conda activate TalkTrain
cd TalkTrain
gradio gradio_app.py
```

#### Test Pipeline

For testing the QG -> TTS -> FA pipeline, run  
``` bash 
python llm+tts+avatar_example.py 
``` 


## Issues, Limitations

You need an Alibaba cloud account and services initiated to test this out. A recorded demo is available on [YouTube](https://youtu.be/Na4XdjN_FaM?si=9K7TArx8PfI4t0jw').

If you run into QS error , setting this environment variable solves this.
```bash 
export QT_QPA_PLATFORM=offscreen 
``` 



## Acknowledgements

TalkTrain builds on existing technologies. We are grateful for training session provided by Alibaba Cloud that facilitated using their platform and their consistent support through the development of this project.

- Question Generation(QG): <a href=''> Alibaba Tongyi Qianwen LLM </a> 
- Automatic Speech Recognition (ASR): <a href='https://openai.com/research/whisper'> OpenAI whisper </a>   
- TTS: <a href='https://www.alibabacloud.com/help/en/intelligent-speech-interaction/latest/activate-service#topic-2572187'> Alibaba Intelligent Speech Interaction </a>  
- Avatar Animation: <a href='https://github.com/OpenTalker/SadTalker'> SadTalker </a>  


