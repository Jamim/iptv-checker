#!/usr/bin/env python3

import m3u8
import re
import traceback
from ffmpy import FFprobe
from urllib.error import HTTPError
from subprocess import PIPE
from sys import stdout
from termcolor import colored


__all__ = ['check_playlist', 'check_channel']


ERASE_LINE = '\033[K'


def check_channel(channel, verbose=False):
	title = channel.title

	def print_failed():
		print('\r{}{:22} {}'.format(ERASE_LINE, title, colored('FAILED', 'red', attrs=['bold'])))

	try:
		print('{:22} checking'.format(title), end='')
		stdout.flush()
		channel_uri = channel.absolute_uri
		try:
			channel_playlist = m3u8.load(channel_uri)
		except HTTPError as error:
			print_failed()
			if verbose:
				print(colored(channel_uri, 'red'))
				print(error)
				print()
			return False

		segment_uri = channel_playlist.segments[-1].absolute_uri
		ffprobe = FFprobe(inputs={segment_uri: '-v warning'})
		errors = ffprobe.run(stderr=PIPE)[1].decode('utf-8')
		if errors:
			print_failed()
			if verbose:
				print(colored(channel_uri, 'green'))
				print(colored(segment_uri, 'red'))
				print(errors)
			return False
	except KeyboardInterrupt as interrupt:
		raise interrupt
	except:
		print_failed()
		if verbose:
			traceback.print_exc()
		return False

	print('\r{}{:22} {}'.format(ERASE_LINE, title, colored('OK', 'green', attrs=['bold'])))
	return True


def check_playlist(playlist_uri, stop_on_fail=False, verbose=False):
	with open(playlist_uri) as playlist_file:
		playlist_data = re.sub(' cn-id=.+,', ',', playlist_file.read())
	playlist = m3u8.loads(playlist_data)
	all_ok = True
	for channel in playlist.segments:
		result = check_channel(channel, verbose)
		stdout.flush()
		if stop_on_fail:
			if not result:
				return False
		else:
			all_ok &= result
	return all_ok


def main(args):
	if args.verbose:
		import os
		if os.getenv('ANSI_COLORS_DISABLED') is None:
			os.putenv('AV_LOG_FORCE_COLOR', '1')
	try:
		if check_playlist(args.playlist_uri, args.stop_on_fail, args.verbose):
			return 0
	except KeyboardInterrupt:
		print()
	return 1


if __name__ == '__main__':
	from argparse import ArgumentParser
	parser = ArgumentParser(description='IPTV playlist checker.')
	parser.add_argument('playlist_uri', type=str, help='playlist for check')
	parser.add_argument(
		'-s', '--stop-on-fail', dest='stop_on_fail', action='store_true', default=False, help='stop on first fail')
	parser.add_argument(
		'-v', '--verbose', dest='verbose', action='store_true', default=False, help='print additional info on fail')
	exit(main(parser.parse_args()))
