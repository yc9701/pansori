from pytube import YouTube
from pytube.helpers import safe_filename

import pysubs2

from pydub.playback import play
from pydub import AudioSegment

import sys, os
from pathlib import Path

import argparse
from urllib.parse import parse_qs, urlparse

data_path = "./data" # setting the path for the videos to be downloaded

def ingest_dataset(yt_uri): # function for ingesting when given a url
	# Use vid as the diretory name for download and processing
	vids = parse_qs(urlparse(yt_uri).query, keep_blank_values=True).get('v')
	vid = None if vids == None else vids[0]

	v_dir = os.path.join(data_path, vid)

	try:
		# Get information on the YouTube content
		yt = YouTube(yt_uri)

		os.makedirs(v_dir, exist_ok=True)

		# Filename for audio stream (.mp4) and subtitle (.srt) files
		audio = os.path.join(v_dir, vid + '.mp4')
		subtitle = os.path.join(v_dir, vid + '.srt')

		if Path(audio).exists() and Path(subtitle).exists():
			sys.exit(1)

		# Download subtitle and write to an .srt file
		subtitle_content = yt.captions.get_by_language_code('ko')
		subtitle_file = open(subtitle, 'w')
		subtitle_file.write(subtitle_content.generate_srt_captions())

		# Download audio stream
		# download() auto appends file extension (.mp4)
		yt.streams.filter(only_audio=True, subtype='mp4').first().download(
			output_path=v_dir, filename=vid)

	except:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		exc_file = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(exc_type, exc_file, exc_tb.tb_lineno)
		sys.exit(1)

# Executing the function
if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		description=__doc__,
		formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument(
		'path', help="URL of the video file to make speech recognition corpus from")

	args = parser.parse_args()

	if args.path.startswith('https://'):
		ingest_dataset(args.path)
	else:
		print("URL of the video file should start with https://")
		sys.exit(1)