from pytube import YouTube
from pytube.helpers import safe_filename

import pysubs2

from pydub.playback import play
from pydub import AudioSegment

# Utilizing Google Cloud Speech-to-Text API
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

import argparse
from urllib.parse import parse_qs, urlparse

import sys, os, io, shutil
import re

def build_phrase_hint(filename):
	with open(filename, 'r') as f:
		hints = f.read().split()
		f.close()
		return hints

# Comparing existing file with Google Cloud output
def compare_speech(fname1, fname2):
	f1 = open(fname1, 'r')
	f2 = open(fname2, 'r')
	s1 = f1.read()
	s2 = f2.read()
	f1.close()
	f2.close()
	return re.sub("\s*", "", s1) == re.sub("\s*", "", s2)

data_path = "./data"

def validate_dataset(yt_uri):
	# Use vid as the diretory name for download and processing
	vids = parse_qs(urlparse(yt_uri).query, keep_blank_values=True).get('v')
	vid = None if vids == None else vids[0]
	dir = os.path.join(data_path, vid)

	# Get information on the YouTube content
	try:
		yt = YouTube(yt_uri)
	except:
		e = sys.exc_info()[0]
		print("Exception: {}".format(e))
		sys.exit(1)

	# Creating array of wav files
	files = []
	for file in os.listdir(dir):
		if file.endswith('.wav'):
			files.append(file)
	files.sort()

	for file in files:
		event_no = os.path.splitext(os.path.basename(file))[0]
		subtitle = os.path.join(dir, event_no + 's.txt')
		transcript = os.path.join(dir, event_no + 't.txt')

		# Printing process and testing files
		try:
			file_path = os.path.join(dir, file)
			print(file_path)
			audio_file = io.open(file_path, 'rb')
			audio_content = audio_file.read()
			audio_file.close()

			audio = types.RecognitionAudio(content=audio_content)
			config = types.RecognitionConfig(
				encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
				speech_contexts=[{"phrases": build_phrase_hint(subtitle)}],
				language_code='ko-kr')

			client = speech.SpeechClient()
			response = client.recognize(config, audio)

			subtitle_file = io.open(subtitle, 'r')
			transcript_file = io.open(transcript, 'w')

			# Determining appropriateness of existing subtitle
			for result in response.results:
				print(u"Subtitle: {}".format(subtitle_file.read()))
				print(u"Transcript: {}".format(result.alternatives[0].transcript))
				print("Confidence: {}".format(result.alternatives[0].confidence))

				try:
					transcript_file.write(result.alternatives[0].transcript)
				except:
					exc_type, exc_obj, exc_tb = sys.exc_info()
					exc_file = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
					print(exc_type, exc_file, exc_tb.tb_lineno)
					sys.exit(1)

			subtitle_file.close()
			transcript_file.close()

			# Moving appropriate files to 'valid' dir
			print(compare_speech(subtitle, transcript))
			if compare_speech(subtitle, transcript):
				valid = os.path.join(dir, "valid")
				if not os.path.exists(valid):
					os.makedirs(valid)
				shutil.move(file_path, valid)
				shutil.move(subtitle, valid)
				shutil.move(transcript, valid)

		except:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			exc_file = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(exc_type, exc_file, exc_tb.tb_lineno)
			sys.exit(1)

# Executing function
if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		description=__doc__,
		formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument(
		'path', help="URL of the video file to make speech recognition corpus from")

	args = parser.parse_args()

	if args.path.startswith('https://'):
		validate_dataset(args.path)
	else:
		print("URL of the video file should start with https://")
		sys.exit(1)
