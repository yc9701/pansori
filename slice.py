from pytube import YouTube
from pytube.helpers import safe_filename

import pysubs2

from pydub.playback import play
from pydub import AudioSegment

import sys, os
import string

import argparse
from urllib.parse import parse_qs, urlparse

data_path = "./data"

def slice_dataset(yt_uri):
	# Use vid as the diretory name for download and processing
	vids = parse_qs(urlparse(yt_uri).query, keep_blank_values=True).get('v')
	vid = None if vids == None else vids[0]
	dir = os.path.join(data_path, vid)

	try:
		# Get information on the YouTube content
		yt = YouTube(yt_uri)

		# Filename for audio stream (.mp4) and subtitle (.srt) files
		audio = os.path.join(data_path, vid + ".mp4")
		subtitle = os.path.join(data_path, vid + ".srt")

		audio_content = AudioSegment.from_file(audio, format='mp4')
		subtitle_content = pysubs2.load(subtitle)

		punctuation_filter = str.maketrans('', '', string.punctuation)

		if not os.path.exists(dir):
			os.makedirs(dir)
			os.makedirs(os.path.join(dir, "valid"))

		for index, event in enumerate(subtitle_content):

			try:
				ev_subtitle = os.path.join(dir, str(index).zfill(4) + 's.txt')
				ev_audio = os.path.join(dir, str(index).zfill(4) + '.wav')

				ev_subtitle_file = open(ev_subtitle, 'w')
				ev_subtitle_file.write(event.text.translate(punctuation_filter))

				ev_audio_content = audio_content[event.start:event.end]
				ev_audio_content = ev_audio_content.set_channels(1)
				ev_audio_content.export(ev_audio, format='wav')

			except:
				exc_type, exc_obj, exc_tb = sys.exc_info()
				exc_file = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
				print(exc_type, exc_file, exc_tb.tb_lineno)
				sys.exit(1)

	except:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		exc_file = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(exc_type, exc_file, exc_tb.tb_lineno)
		sys.exit(1)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		description=__doc__,
		formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument(
		'path', help="URL of the video file to make speech recognition corpus from")

	args = parser.parse_args()
	
	if args.path.startswith('https://'):
		slice_dataset(args.path)
	else:
		print("URL of the video file should start with https://")
		sys.exit(1)
