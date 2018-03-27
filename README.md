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
python mrip.py -i <inputfile>
OR
python mrip.py -q <artist + song name>
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

## Advanced Options
An output directory may be specified with the '-o' flag. On Mac, using the '-o' flag with the following folder will automatically add the song to iTunes.

``` 
python mrip.py -o /Users/<username>/Music/iTunes/iTunes\ Media/Automatically\ Add\ to\ iTunes.localized 
```

Alternatively, adding the following to function to your ~/.bashrc file will allow you to add songs to iTunes simple by typing `addsong -q Ariana Grande Moonlight`. Make sure to specify the path to your MRip directory and your username.

```bash
addsong() {
    pushd /path/to/mrip_directory/ > /dev/null;
    python mrip.py -o /Users/<username>/Music/iTunes/iTunes\ Media/Automatically\ Add\ to\ iTunes.localized  $@;
    popd > /dev/null;
}
```
For other config options, run `python mrip.py -h`.
