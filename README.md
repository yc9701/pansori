# Pansori

Pansori is a program for creating an ASR corpus from YouTube videos with audio and subtitle data. It can be used for any language when the specifier is set in the code.

This program currently consists of three modules:

- Ingest: Takes in the YouTube video information and reads it to output an audio file and a text file of the subtitles with timing information
- Slice: Slices the audio file based on the timing information within the subtitle file and assigns the appropriate subtitle to the audio slice
- Validate: Compares the subtitle information to a transcription obtained through using the Google Cloud Speech-to-Text API

This program automatically creates audio segments with aligned text labels by utilizing the timing information stored in the subtitle data to build the corpus faster.

The program is currently being used for a project to create a Korean language corpus and can be used for other languages.

