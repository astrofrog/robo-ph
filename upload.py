import shutil
import subprocess

DROPBOX_DIR = os.path.expanduser("~/Dropbox/Public/robo-ph/")

date = now.strftime("%Y-%m-%d")

shutil.copy(date + '.m4a', os.path.join(DROPBOX_DIR, date + '.m4a'))
shutil.copy('rss/combined.rss', os.path.join(DROPBOX_DIR, 'roboph.rss'))
subprocess.call('git add rss/combined.rss ; git commit rss/combined.rss', shell=True)
