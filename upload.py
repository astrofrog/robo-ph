import os
import shutil
import subprocess

DROPBOX_DIR = os.path.expanduser("~/Dropbox/Public/robo-ph/")

subprocess.call('rsync -a final/ ~/Dropbox/Public/robo-ph/', shell=True)
shutil.copy('rss/combined.rss', os.path.join(DROPBOX_DIR, 'roboph.rss'))
subprocess.call('git add rss/*.rss ; git commit -m "Automated RSS feed commit"', shell=True)
