# Pansori
Pansori is a program for creating an automatic speech recognition (ASR) corpus from online videos with audio and subtitle data.
## Overview
![alt text](https://storage.googleapis.com/pansori/img/pansori_overview.png)

It consists of 4 pipeline stages as shown in the diagram above: ingest, align, transform and validate.

### Ingest
Online video contents consist of multiple media streams for different screen resolutions and audio-only playback; hand-transcribed subtitle information can also be retrieved if available. Pansori downloads the audio and subtitle streams from online videos as mp4 and srt files, respectively.
### Align
The subtitles contain segmented text and timing information which corresponds to the audio contents of the associated video. With the timing information, it is possible to segment the audio stream to make a matching pair of audio and text fragments for an ASR corpus.

However, inaccuracies can be introduced to the segmented contents because the timing information might be determined not only by audio contents but also by scene changes in the video. In addition, they can also arise from unintentional slicing of audio stream at word boundaries in fast speeches and when substantial ambient noise such as applause is present. To fix these inaccuracies, we used [finetuneas](https://github.com/ozdefir/finetuneas), a GUI tool to help find correct alignment between audio and text. We are currently moving to a fully automated forced alignment approach in order to further simplify this stage.
### Transform
The aligned audio stream and subtitle data are then processed with the following transformations specific to data types:
* Audio stream: segmentation, lossless compression
* Subtitle data: normalization, punctuation removal, removal of non-speech text (such as the description of audience response or ambient noise)

### Validate
Although the audio stream and subtitle data are force-aligned with each other, there are also inherent discrepancies between the two. This can come from one or more of the following: inaccurate transcriptions, ambiguous pronunciations, and non-ideal audio conditions (like ambient noise or poor recording quality). To increase the quality of the corpus, the corpus needs to be refined by filtering out inaccurate audio and subtitle pairs.

Previous approaches relied on custom ASR models for corpus validation and refinement; however, they are not easily created for many languages, especially for those without existing corpora. In Pansori, we used a new approach through a cloud-based ASR; we chose the Google Cloud Speech-to-Text API since it provides the highest quality ASR services in more than 120 languages. Cloud services make the development of corpus generation much faster and easier since we can just set up the cloud service rather than create custom ASR engines with acoustic and language models in different languages.

---
The program can be modified for use in videos subtitled in any language available in the Google API.

## Installation
Clone repository:
```bash
$ git clone https://github.com/yc9701/pansori
```

Install *pytube*, a library for downloading YouTube videos.
```bash
$ pip install pytube
```

Install *pysubs2*, a library for editing subtitle files.
<small>\*Currently, pysubs2 runs only with Python 3.6; on Python 3.7, this library does not work</small>
```bash
$ pip install pysubs2
```

Install *pydub*, a library for manipulating audio.
<small>\*Only necessary if wishing for audio playback when validating audio</small>
```bash
$ pip install pydub
```

The Google Cloud Speech API is also required for validate.py (an account is required).
* [Installation and use guide](https://cloud.google.com/speech-to-text/docs/quickstart-gcloud)
