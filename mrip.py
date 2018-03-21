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

def download_all(songs, save_dir):
    for artist in songs:
        for song in songs[artist]:
            metadata = get_metadata(artist + " " + song)
            if metadata == None:
                debug(song + " - " + artist + " not found on iTunes!\n")
                continue

            # TODO: optimize this
            youtube_query = metadata['trackName'] + " " + metadata['artistName'] + " lyrics"
            album_cover_query = metadata['collectionName'] + " " + metadata['artistName'] + " album cover"
            file_name = "".join(metadata['trackName'].split())+".mp3"

            if file_name in os.listdir(save_dir):
                debug("Skipping " + metadata['trackName'] + "!\n")
                continue

            file_name = save_dir+file_name

            debug(metadata['trackName'] + " - " + metadata['artistName'] + "... ")


            # download mp3, albumcover
            download_youtube(youtube_query, os.path.join(os.getcwd(), save_dir))
            scrape_img(album_cover_query, os.path.join(os.getcwd(), save_dir))


            # create finished mp3
            command = ['lame', save_dir+"song.mp3", file_name, "--quiet",
                    "--tt", metadata['trackName'],
                    "--ta", metadata['artistName'],
                    "--tl", metadata['collectionName'],
                    "--ty", metadata['releaseDate'][:4],
                    "--tn", str(metadata['trackNumber'])+"/"+str(metadata['trackCount']),
                    "--tg", metadata['primaryGenreName'],
                    "--ti", save_dir+"img.jpg"]

            output = check_output(command)

            # clean up generated files
            os.remove(save_dir+"img.jpg")
            os.remove(save_dir+"song.mp3")

            debug("done!\n")

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
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    if not os.path.isfile(input_file):
        perror("ERROR: "+input_file+" not found!\n")
        sys.exit(1)

    # parse the input file
    artist_songs = parse_input(input_file)
    #resolve_albums(artist_songs)

    # download songs
    download_all(artist_songs, output_dir)

    
