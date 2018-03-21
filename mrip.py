import argparse
import sys, os
from mrip_web import download_youtube, scrape_img, get_metadata

DEFAULT_OUTPUT = 'output/'

# writes to stderr
def perror(message):
    sys.stderr.write(message)

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

def download_all(songs, save_dir):
    for artist in songs:
        for song in songs[artist]:
            metadata = get_metadata(artist + " " + song)

            # TODO: optimize this
            youtube_query = metadata['trackName'] + " " + metadata['artistName']
            album_cover_query = metadata['collectionName'] + " " + metadata['artistName'] + " album cover"
            print(youtube_query)
            print(album_cover_query)

            # download mp3, albumcover
            download_youtube(youtube_query, os.path.join(os.getcwd(), save_dir))
            scrape_img(album_cover_query, os.path.join(os.getcwd(), save_dir))

            sys.exit(1)
        sys.exit(1)

if __name__ == '__main__':
    # format command line arguments
    parser = argparse.ArgumentParser(description='Download and format mp3 files.')
    parser.add_argument('inputfile', type=str, nargs=1,
            help='the input file of songs')
    parser.add_argument('-o', metavar='output_directory', type=str, nargs=1,
            help='the output directory, output/ by default')
    args = parser.parse_args()

    # get input and output files/directories
    input_file = args.inputfile[0]
    if args.o:
        if args.o[0].endswith("/"):
            output_dir = args.o[0]
        else:
            output_dir = args.o[0]+"/"
    else:
        output_dir = DEFAULT_OUTPUT
        perror("WARNING: using default output directory -> "+DEFAULT_OUTPUT+"\n")
    output_dir = args.o[0]+'/' if args.o else DEFAULT_OUTPUT

    # verify input/output directories
    if (os.path.isdir(output_dir)):
        if os.listdir(output_dir):
            perror("ERROR: "+output_dir+
                    " is not empty! Stash your saved results!\n")
            sys.exit(1)
    else:
        os.mkdir(output_dir)

    if not os.path.isfile(input_file):
        perror("ERROR: "+input_file+" not found!\n")
        sys.exit(1)

    # parse the input file
    artist_songs = parse_input(input_file)
    #resolve_albums(artist_songs)

    # download songs
    download_all(artist_songs, output_dir)

    
