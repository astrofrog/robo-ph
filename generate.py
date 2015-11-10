import os
import glob
import random
import subprocess
from datetime import datetime, timedelta

from roboph import VOICES, get_latest_articles, speak, BANNER

from utils import weekdays

print(BANNER)

# The start date is used to determine the track number. This number is one on
# the date below, and is then incremented by one for each weekday.
START_DATE = datetime(2015, 11, 5)

NOW = datetime.now()
DATE = NOW.strftime("%Y-%m-%d")
YEAR = NOW.year
TMPDIR = os.path.join('tmp', DATE)

TRACK = weekdays(START_DATE, NOW)

FINALDIR = 'final'

# Make sure voices are deterministic for a given date
random.seed(DATE)

if os.path.exists(TMPDIR):
    raise ValueError("Directory {0} already exists".format(TMPDIR))
else:
    os.makedirs(TMPDIR)

OUTPUT_FILE = os.path.join(FINALDIR, DATE + '.m4a')

if not os.path.exists(FINALDIR):
    os.makedirs(FINALDIR)

if os.path.exists(OUTPUT_FILE):
    raise ValueError("File {0} already exists".format(OUTPUT_FILE))

HEADER = """;FFMETADATA1
title=robo-ph: {date}
artist=robo-ph
album=robo-ph
track={track}
date={year}
genre=Podcast
copyright=(c) J.E.G. Peek, Thomas Robitaille, Katie Mack & Arna Karick

"""

CHAPTER = """[CHAPTER]
TIMEBASE=1/1000
START={start:d}
END={end:d}
title={title}
"""

total_length = 0

def add_chapter(fileobj, title, length):
    global total_length
    fileobj.write(CHAPTER.format(start=int(total_length), end=int(total_length + length), title=title))
    total_length += length

print("Getting latest articles")
latest_articles = get_latest_articles()

print("Randomizing")
random.shuffle(latest_articles)

print("Producing audio files")

file_list = open(os.path.join(TMPDIR, 'files'), 'w')
file_meta = open(os.path.join(TMPDIR, 'metadata'), 'w')

file_meta.write(HEADER.format(date=DATE, track=TRACK, year=YEAR))

text = "Welcome to robo p h, we have {0} papers today, so let's get started! [[slnc 2000]]".format(len(latest_articles))
voice = random.choice(VOICES)
length = speak(text, voice, os.path.join(TMPDIR, 'intro.aiff'))
add_chapter(file_meta, 'Intro', length)
file_list.write("file 'intro.aiff'\n")

for article in latest_articles:

    # Select voice at random
    voice = random.choice(VOICES)

    # Make article into voice file
    output_file = os.path.join(TMPDIR, article.identifier + '.aiff')
    length = article.to_audio_file(output_file, voice=voice)

    add_chapter(file_meta, article.identifier, length)
    file_list.write("file '{0}'\n".format(os.path.basename(output_file)))

text = "This podcast was produced by Josh Peek, Tom Robeet Eye, Katie Mack, and Arna Karick, at dotAstronomy seven, in Sydney! Thank you for listening!"
voice = random.choice(VOICES)
length = speak(text, voice, os.path.join(TMPDIR, 'outro.aiff'))
add_chapter(file_meta, 'Outro', length)
file_list.write("file 'outro.aiff'\n")

text = "[[slnc 3000]] Kill all humans."
length = speak(text, 'Bruce', os.path.join(TMPDIR, 'epilogue.aiff'))
add_chapter(file_meta, 'Epilogue', length)
file_list.write("file 'epilogue.aiff'\n")

file_list.close()
file_meta.close()

f_log = open('log.txt', 'w')

print("Concatenating to single file")
subprocess.call('ffmpeg -f concat -i {0}/files {0}/combined.mp3'.format(TMPDIR), shell=True, stdout=f_log, stderr=f_log)

print("Adding chapters")
subprocess.call('ffmpeg -i {0}/combined.mp3 -i {0}/metadata -map_metadata 1 -c:a copy -id3v2_version 3 -write_id3v1 1 {0}/combined2.mp3'.format(TMPDIR), shell=True, stdout=f_log, stderr=f_log)

print("Converting to M4A")
subprocess.call('ffmpeg -i {0}/combined2.mp3 -strict -2  -b:a 50k {1}'.format(TMPDIR, OUTPUT_FILE), shell=True, stdout=f_log, stderr=f_log)

print("Adding album art")
subprocess.call('AtomicParsley {0} --artwork robo-ph-cover_art.jpg'.format(OUTPUT_FILE), shell=True, stdout=f_log, stderr=f_log)
subprocess.call('AtomicParsley {0} --artwork robo-ph-cover_art.jpg --overWrite'.format(OUTPUT_FILE), shell=True, stdout=f_log, stderr=f_log)

f_log.close()

def concatenate_files(filenames, output_file):
    with open(output_file, 'w') as fout:
        for filename in filenames:
            with open(filename, 'r') as fin:
                fout.write(fin.read())

print("Creating RSS entry")

# Get GMT publication date
now = datetime.utcnow()  # GMT
pubdate = now.strftime("%a, %-d %b %Y %H:%M:%S GMT")

# Get duration in minutes:seconds
delta = timedelta(seconds=total_length / 1000)
duration = (datetime(1900,1,1) + delta).strftime("%H:%M:%S")

template = open('rss/template.rss', 'r').read()
with open('rss/{0}.rss'.format(DATE), 'w') as f:
    f.write(template.format(date=DATE, filename=DATE + '.m4a', pubdate=pubdate, duration=duration))

concatenate_files(['rss/header.rss'] + sorted(glob.glob('rss/????-??-??.rss')) + ['rss/footer.rss'], 'rss/combined.rss')
