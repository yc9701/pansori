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

def slice_dataset(yt_uri, align_padding, out_stage):
	# Use vid as the diretory name for download and processing
	vids = parse_qs(urlparse(yt_uri).query, keep_blank_values=True).get('v')
	vid = None if vids == None else vids[0]

	v_dir = os.path.join(data_path, vid)
	out_dir = os.path.join(v_dir, out_stage)

	try:
		# Get information on the YouTube content
		yt = YouTube(yt_uri)

		# Filename for audio stream (.mp4) and subtitle (.srt) files
		audio = os.path.join(v_dir, vid + ".mp4")
		subtitle = os.path.join(v_dir, vid + ".srt")

		# Retrieving subtitle information
		audio_content = AudioSegment.from_file(audio, format='mp4')
		subtitle_content = pysubs2.load(subtitle)

		punctuation_filter = str.maketrans('', '', string.punctuation)

		os.makedirs(out_dir, exist_ok=True)

		# Writing to file
		for index, event in enumerate(subtitle_content):

			try:
				if event.text.translate(punctuation_filter) == "":
				 	continue
				
				ev_subtitle = os.path.join(out_dir, str(index).zfill(4) + '.txt')
				ev_audio = os.path.join(out_dir, str(index).zfill(4) + '.wav')

				ev_subtitle_file = open(ev_subtitle, 'w')
				ev_subtitle_file.write(event.text.translate(punctuation_filter))

				ev_audio_content = audio_content[
					max(0, event.start - align_padding):
					min(event.end + align_padding, len(audio_content))]
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

# Executing the function
if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		description=__doc__,
		formatter_class=argparse.RawDescriptionHelpFormatter)

	parser.add_argument(
		'path', help="URL of the video file to make speech recognition corpus from")

	parser.add_argument(
		'-o', '--output', type=int, default=00,
		help="output pipeline stage")

	parser.add_argument(
		'-a', '--align', type=int, default=1000,
		help="padding for start / end alignment (in msec)")

	args = parser.parse_args()
	
	if args.path.startswith('https://'):
		if args.output >= 0:
			slice_dataset(args.path, args.align, str(args.output).zfill(2))
		else:
			print("Pipeline stages should not be negative")
			sys.exit(1)
	else:
		print("URL of the video file should start with https://")
		sys.exit(1)
