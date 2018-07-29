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

def download_query(itunes_query, save_dir, fill, youtube_query_manual=None):
        metadata = get_metadata(itunes_query)
        if metadata == None or "collectionName" not in metadata:
            debug(itunes_query + " not found on iTunes!\n")
            if not fill:
                return
            else:
                metadata = dict()
                print("Enter manually! (Press enter for nothing) \n")
                resp = input("Enter track name: ")
                if resp:
                    metadata['trackName'] = resp
                resp = input("Enter artist name: ")
                if resp:
                    metadata['artistName'] = resp
                resp = input("Enter album name: ")
                if resp:
                    metadata['collectionName'] = resp
                resp = input("Enter release year: ")
                if resp:
                    metadata['releaseDate'] = resp
                resp = input("Enter track number: ")
                if resp:
                    metadata['trackNumber'] = resp
                resp = input("Enter genre: ")
                if resp:
                    metadata['primaryGenreName'] = resp

        # TODO: optimize this
        youtube_query = metadata['trackName'] + " " + metadata['artistName'] + " topic lyrics"
        album_cover_query = (metadata['collectionName'] if 'collectionName' in metadata else metadata['trackName']) + " " + metadata['artistName'] + " itunes"
        file_name = "".join(metadata['trackName'].split())+".mp3"

        if file_name in os.listdir(save_dir):
            debug("Skipping " + metadata['trackName'] + "!\n")
            return

        file_name = save_dir+file_name

        debug(metadata['trackName'] + " - " + metadata['artistName'] + "... ")


        # download mp3, albumcover
        download_youtube(youtube_query, os.getcwd(), link=youtube_query_manual)
        scrape_img(album_cover_query, os.getcwd())


        # create finished mp3
        command = ['lame', ".song.mp3", file_name, "--quiet", "--ti", ".img.jpg"]
        if 'trackName' in metadata:
            command.extend(("--tt", metadata['trackName']))
        if 'artistName' in metadata:
            command.extend(("--ta", metadata['artistName']))
        if 'collectionName' in metadata:
            command.extend(("--tl", metadata['collectionName']))
        if 'releaseDate' in metadata:
            command.extend(("--ty", metadata['releaseDate'][:4]))
        if 'trackNumber' in metadata:
            command.extend(("--tn", str(metadata['trackNumber'])+"/"+str(metadata['trackCount'])))
        if 'primaryGenreName' in metadata:
            command.extend(("--tg", metadata['primaryGenreName']))

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
    parser.add_argument('-f', '--fill', dest = 'fill', action="store_true",
            help='flag specifying whether user would like to manually fill information not on iTunes')
    parser.add_argument('-y', '--youtube', dest = 'youtube', action="store", nargs='+',
            help='specifiy url of youtube video')
    parser.set_defaults(fill=False)
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

        for artist in artist_songs:
            for song in artist_songs[artist]:
                if args.youtube:
                    download_query(artist + " " + song, output_dir, args.fill, youtube_query_manual=" ".join(args.youtube))
                else:
                    download_query(artist + " " + song, output_dir, args.fill)
    elif args.query:
        if args.youtube:
            download_query(" ".join(args.query), output_dir, args.fill, youtube_query_manual=" ".join(args.youtube))
        else:
            download_query(" ".join(args.query), output_dir, args.fill)


    
