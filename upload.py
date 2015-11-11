import os
import time
import shutil
import subprocess

DROPBOX_DIR = os.path.expanduser("~/Dropbox/Public/robo-ph/")

subprocess.call('rsync -a final/ {0}'.format(DROPBOX_DIR), shell=True)
shutil.copy('rss/combined.rss', os.path.join(DROPBOX_DIR, 'roboph.rss'))

time.sleep(60)

subprocess.call('git add rss/*.rss ; git commit -m "Automated RSS feed commit" ; git push origin master', shell=True)
