import os
import glob
import shutil
import random
import datetime
import subprocess

from roboph import VOICES, get_latest_articles, speak, BANNER

DROPBOX_DIR = os.path.expanduser("~/Dropbox/Public/go-the-ph-to-sleep/")

print(BANNER)

track = 1
now = datetime.datetime.now()
date = now.strftime("%Y-%m-%d")
year = now.year
directory = date

if os.path.exists(directory):
    raise ValueError("Directory {0} already exists".format(directory))
else:
    os.mkdir(directory)

if os.path.exists(directory + 'm4a'):
    raise ValueError("File {0} already exists".format(directory + 'm4a'))

HEADER = """;FFMETADATA1
title=go-the-ph-to-sleep: {date}
artist=go-the-ph-to-sleep
album=go-the-ph-to-sleep
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

file_list = open(os.path.join(directory, 'files'), 'w')
file_meta = open(os.path.join(directory, 'metadata'), 'w')

file_meta.write(HEADER.format(date=date, track=track, year=year))

text = "Welcome to go the PH to sleep, we have {0} papers today, so get cosy! [[slnc 2000]]".format(len(latest_articles))
voice = random.choice(VOICES)
length = speak(text, voice, os.path.join(directory, 'intro.aiff'))
add_chapter(file_meta, 'Intro', length)
file_list.write("file 'intro.aiff'\n")

for article in latest_articles:

    # Select voice at random
    voice = random.choice(VOICES)

    # Make article into voice file
    output_file = os.path.join(directory, article.identifier + '.aiff')
    length = article.to_audio_file(output_file, voice=voice)

    add_chapter(file_meta, article.identifier, length)
    file_list.write("file '{0}'\n".format(os.path.basename(output_file)))

text = "This podcast was produced by Josh Peek, Tom Robeet Eye, Katie Mack, and Arna Karick, at dotAstronomy seven, in Sydney! Thank you for listening!"
voice = random.choice(VOICES)
length = speak(text, voice, os.path.join(directory, 'outro.aiff'))
add_chapter(file_meta, 'Outro', length)
file_list.write("file 'outro.aiff'\n")

text = "[[slnc 3000]] Kill all humans."
length = speak(text, 'Bruce', os.path.join(directory, 'epilogue.aiff'))
add_chapter(file_meta, 'Epilogue', length)
file_list.write("file 'epilogue.aiff'\n")

file_list.close()
file_meta.close()

f_log = open('log.txt', 'w')

print("Concatenating to single file")
subprocess.call('ffmpeg -f concat -i {0}/files {0}/combined.mp3'.format(directory), shell=True, stdout=f_log, stderr=f_log)

print("Adding chapters")
subprocess.call('ffmpeg -i {0}/combined.mp3 -i {0}/metadata -map_metadata 1 -c:a copy -id3v2_version 3 -write_id3v1 1 {0}/combined2.mp3'.format(directory), shell=True, stdout=f_log, stderr=f_log)

print("Converting to M4A")
subprocess.call('ffmpeg -i {0}/combined2.mp3 -strict -2  -b:a 50k {1}.m4a'.format(directory, date), shell=True, stdout=f_log, stderr=f_log)

print("Adding album art")
subprocess.call('AtomicParsley {0}.m4a --artwork gothephtosleep-cover_art.jpg'.format(date), shell=True, stdout=f_log, stderr=f_log)
subprocess.call('AtomicParsley {0}.m4a --artwork gothephtosleep-cover_art.jpg --overWrite'.format(date), shell=True, stdout=f_log, stderr=f_log)

f_log.close()

def concatenate_files(filenames, output_file):
    with open(output_file, 'w') as fout:
        for filename in filenames:
            with open(filename, 'r') as fin:
                fout.write(fin.read())

print("Creating RSS entry")

# Get GMT publication date
now = datetime.datetime.utcnow()  # GMT
pubdate = now.strftime("%a, %-d %b %Y %H:%M:%S GMT")

# Get duration in minutes:seconds
delta = datetime.timedelta(seconds=total_length / 1000)
duration = (datetime.datetime(1900,1,1) + delta).strftime("%H:%M:%S")

template = open('rss/template.rss', 'r').read()
with open('rss/{0}.rss'.format(date), 'w') as f:
    f.write(template.format(date=date, filename=date + '.m4a', pubdate=pubdate, duration=duration))

concatenate_files(['rss/header.rss'] + sorted(glob.glob('rss/????-??-??.rss')) + ['rss/footer.rss'], 'rss/gothephtosleep.rss')

shutil.copy(date + '.m4a', os.path.join(DROPBOX_DIR, date + '.m4a'))
shutil.copy('rss/gothephtosleep.rss', os.path.join(DROPBOX_DIR, 'gothephtosleep.rss'))
subprocess.call('git add rss/gothephtosleep.rss ; git commit rss/gothephtosleep.rss', shell=True)
