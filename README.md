# Pansori
Pansori is a program for creating an ASR corpus from YouTube videos with audio and subtitle data.

## Description
This program currently consists of three modules:

- Ingest: Takes in the YouTube video information and reads it to output an audio file and a text file of the subtitles with timing information
- Slice: Slices the audio file based on the timing information within the subtitle file and assigns the appropriate subtitle to the audio slice
- Validate: Compares the subtitle information to a transcription obtained through using the Google Cloud Speech-to-Text API

This program automatically creates audio segments with aligned text labels by utilizing the timing information stored in the subtitle data to build the corpus faster. It also automatically verifies the audio segments for accuracy using the Google Cloud Speech API.

## Installation
Clone repository:
```bash
$ git clone https://github.com/yc9701/pansori
```

Install *pytube*, a library for downloading YouTube videos.
```bash
$ pip install pytube
```

Install *pysubs*, a library for editing subtitle files.
<small>\*Currently, pysubs2 runs only with Python 3.6; on Python 3.7, this does not work</small>
```bash
$ pip install pysubs2
```

Install *pydub*, a library for manipulating audio.
<small>\*Only necessary if wishing for audio playback</small>
```bash
$ pip install pydub
```

The Google Cloud Speech API is also required for validate.py (an account is required).
* Create a Google Cloud Platform console project and enable the Speech-to-Text API
* Create a service account and download a private key as JSON
* Set the environment variable *GOOGLE_APPLICATION_CREDENTIALS*
* Install and initialize the Cloud SDK
