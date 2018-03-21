# MRip
MRip is a Python tool that downloads and formats mp3s from YouTube with iTunes metadata and album covers. It makes use of the iTunes Search API and scrapes the images and MP3's off of Google Image Search and Youtube respectively.


## Usage
Requires Python3 and the following command line utilities:
* lame
* ffmpeg

Both can be installed with Homebrew on Mac (`brew install lame` and `brew install ffmpeg`).
With the above installed, simply run,

```bash
pip install -r requirements.txt
python mrip.py <inputfile>
```

The input file must be formatted as shown below:

```
Kanye West		<- artist on first line
Monster			<- list of songs following
Ultralight Beam
Stronger
				<- new artist indicated by newline
Taylor Swift
I Knew You Were Trouble
```

For more config options, run `python mrip.py -h`.


## Future Plans
In the future, I'd like to:
* Add an album feature that allows entire albums to be downloaded
* Allow users to manually select the YouTube source from a list
