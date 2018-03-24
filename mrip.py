import argparse
from subprocess import check_output
import sys, os
from mrip_web import download_youtube, scrape_img, get_metadata

DEFAULT_OUTPUT = 'output/'
DEBUG = True
VERBOSE = False


# writes to stdout
def debug(message):
    if DEBUG: 
        sys.stdout.write(message)
        sys.stdout.flush()

# writes to stderr
def perror(message):
    sys.stderr.write(message)
    sys.stderr.flush()

# parses the input file into a dictionary
def parse_input(input_file):
    songs = dict()

    with open(input_file) as f:
        artist = None
        for line in f:
            line = line.strip()
            isEmpty = line == ''

            if artist and isEmpty:
                # switching to next artist
                artist = None
            elif artist and not isEmpty:
                # new song
                if artist in songs:
                    songs[artist].append(line)
                else:
                    songs[artist] = [line]
            elif not artist and not isEmpty:
                # new artist
                artist = line
    return songs

# TODO:resolves albums to list of songs
def resolve_albums(songs):
    for artist in songs:
        realSongs = [s for s in songs[artist] if not s.startswith("ALBUM")]
        albums = [" ".join(s.split(" ")[1:]) for s in songs[artist] if s.startswith("ALBUM")]

def download_query(itunes_query, save_dir):
        metadata = get_metadata(itunes_query)
        if metadata == None or "collectionName" not in metadata:
            debug(itunes_query + " not found on iTunes!\n")
            return

        # TODO: optimize this
        youtube_query = metadata['trackName'] + " " + metadata['artistName'] + " topic lyrics"
        album_cover_query = metadata['collectionName'] + " " + metadata['artistName'] + " album cover"
        file_name = "".join(metadata['trackName'].split())+".mp3"

        if file_name in os.listdir(save_dir):
            debug("Skipping " + metadata['trackName'] + "!\n")
            return

        file_name = save_dir+file_name

        debug(metadata['trackName'] + " - " + metadata['artistName'] + "... ")


        # download mp3, albumcover
        download_youtube(youtube_query, os.getcwd())
        scrape_img(album_cover_query, os.getcwd())


        # create finished mp3
        command = ['lame', ".song.mp3", file_name, "--quiet",
                "--tt", metadata['trackName'],
                "--ta", metadata['artistName'],
                "--tl", metadata['collectionName'],
                "--ty", metadata['releaseDate'][:4],
                "--tn", str(metadata['trackNumber'])+"/"+str(metadata['trackCount']),
                "--tg", metadata['primaryGenreName'],
                "--ti", ".img.jpg"]

        output = check_output(command)

        # clean up generated files
        os.remove(".img.jpg")
        os.remove(".song.mp3")

        debug("done!\n")

if __name__ == '__main__':
    # format command line arguments
    parser = argparse.ArgumentParser(description='Download and format mp3 files.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-q', '--query', type=str, action = "store", nargs="+",
            help="an iTunes query to download")
    group.add_argument('-i', '--inputfile', type=str, action = "store",
            help="an input file with multiple songs")
    parser.add_argument('-o', metavar='output_directory', type=str, nargs=1,
            help='the output directory, output/ by default')
    args = parser.parse_args()

    # get input and output files/directories
    if args.o:
        if args.o[0].endswith("/"):
            output_dir = args.o[0]
        else:
            output_dir = args.o[0]+"/"
    else:
        output_dir = DEFAULT_OUTPUT
        perror("WARNING: using default output directory -> "+DEFAULT_OUTPUT+"\n")
    output_dir = args.o[0]+'/' if args.o else DEFAULT_OUTPUT

    if args.inputfile:
        # parse the input file
        artist_songs = parse_input(args.inputfile)

        #resolve_albums(artist_songs)

        for artist in artist_songs:
            for song in artist_songs[artist]:
                download_query(artist + " " + song, output_dir)
    elif args.query:
        download_query(" ".join(args.query), output_dir)

    
