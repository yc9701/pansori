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
from pathlib import Path
import re, difflib

def build_phrase_hint(filename):
	with open(filename, 'r') as f:
		hints = f.read().split()
		f.close()
		return hints

# Comparing caption subtitle with ASR output 
def exact_match(fname1, fname2):
	f1 = open(fname1, 'r')
	f2 = open(fname2, 'r')
	s1 = f1.read()
	s2 = f2.read()
	f1.close()
	f2.close()

	s1n = re.sub("\s*", "", s1).lower()
	s2n = re.sub("\s*", "", s2).lower()

	if s1n == s2n:
		return True
	else:
		return False

def substring_match(fname1, fname2):
	f1 = open(fname1, 'r')
	f2 = open(fname2, 'r')
	s1 = f1.read()
	s2 = f2.read()
	f1.close()
	f2.close()

	s1n = re.sub("\s*", "", s1).lower()
	s2n = re.sub("\s*", "", s2).lower()

	if s1n in s2n:
		return True
	else:
		return False

def similarity_score(fname1, fname2):
	f1 = open(fname1, 'r')
	f2 = open(fname2, 'r')
	s1 = f1.read()
	s2 = f2.read()
	f1.close()
	f2.close()

	s1n = re.sub("\s*", "", s1).lower()
	s2n = re.sub("\s*", "", s2).lower()

	score = difflib.SequenceMatcher(None, s1n, s2n).ratio()
	return score


data_path = "./data"

def validate_dataset(yt_uri, matching, in_stage, out_stage, src_stage):
	# Use vid as the diretory name for download and processing
	vids = parse_qs(urlparse(yt_uri).query, keep_blank_values=True).get('v')
	vid = None if vids == None else vids[0]

	v_dir = os.path.join(data_path, vid)
	in_dir = os.path.join(v_dir, in_stage)
	out_dir = os.path.join(v_dir, out_stage)

	src_dir = os.path.join(v_dir, src_stage)

	# Get information on the YouTube content
	try:
		yt = YouTube(yt_uri)
	except:
		e = sys.exc_info()[0]
		print("Exception: {}".format(e))
		sys.exit(1)

	# Creating array of wav files
	files = []
	for file in os.listdir(in_dir):
		if file.endswith('.wav'):
			files.append(file)
	files.sort()

	os.makedirs(out_dir, exist_ok=True)

	# Speech client
	client = speech.SpeechClient()

	for file in files:
		event_no = os.path.splitext(os.path.basename(file))[0]
		subtitle = os.path.join(in_dir, event_no + '.txt')
		transcript = os.path.join(in_dir, event_no + 't.txt')

		subtitle_src = os.path.join(src_dir, event_no + '.txt')
		transcript_src = os.path.join(src_dir, event_no + 't.txt')

		if Path(subtitle_src).exists() == False:
			continue

		# Printing process and testing files
		try:
			file_path = os.path.join(in_dir, file)
			print(file_path)
			audio_file = io.open(file_path, 'rb')
			audio_content = audio_file.read()
			audio_file.close()

			file_path_src = os.path.join(src_dir, file)

			audio = types.RecognitionAudio(content=audio_content)
			config = types.RecognitionConfig(
				encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
				speech_contexts=[{"phrases": build_phrase_hint(subtitle)}],
				language_code='ko-kr')

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

			# Moving appropriate files to output pipeline stage
			if matching == 'exact':
				result = exact_match(subtitle, transcript)
				score = 1.0 if result == True else 0.0
			elif matching == 'similarity':
				score = similarity_score(subtitle, transcript)
				result = score >= 0.9 
			else: # matching == 'subs' or else
				result = substring_match(subtitle, transcript)
				score = 1.0 if result == True else 0.0

			print("Result: {}, Score: {}".format(result, score))
			print("")

			if result == True:
				shutil.move(file_path_src, out_dir)
				shutil.move(subtitle_src, out_dir)
				shutil.move(transcript_src, out_dir)

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

	parser.add_argument(
		'-m', '--match', default='subs', choices=['exact', 'subs', 'similarity'],
		help="matching method--exact, substring, similarity (default: %(default)s)")

	parser.add_argument(
		'-i', '--input', type=int, default=98, help="input pipeline stage")

	parser.add_argument(
		'-o', '--output', type=int, default=99, help="output pipeline stage")

	parser.add_argument(
		'-s', '--source', type=int, default=00, help="source pipeline stage")

	args = parser.parse_args()

	if args.path.startswith('https://'):
		if args.input >= 0 and args.output >= 0:
			validate_dataset(args.path, args.match,
				str(args.input).zfill(2), 
				str(args.output).zfill(2), 
				str(args.source).zfill(2))
		else:
			print("Pipeline stages should not be negative")
			sys.exit(1)
	else:
		print("URL of the video file should start with https://")
		sys.exit(1)