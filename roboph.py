from __future__ import unicode_literals, print_function, division

import os
import aifc
import requests
import subprocess
from AppKit import NSSpeechSynthesizer, NSURL
import xml.etree.ElementTree as ElementTree
from bs4 import BeautifulSoup

VALID_VOICES = [str(x.replace('com.apple.speech.synthesis.voice.', '')) for x in NSSpeechSynthesizer.availableVoices()]
VOICES =['lee.premium', 'fiona.premium', 'emily.premium', 'Alex', 'tom.premium', 'jill.premium', 'sangeeta.premium']

ARXIV_URL = "http://export.arxiv.org/rss/astro-ph"

JINGLE = {
    '[astro-ph.CO]': 'jingles/CO.aiff',
    '[astro-ph.EP]': 'jingles/EP.aiff',
    '[astro-ph.GA]': 'jingles/GA.aiff',
    '[astro-ph.HE]': 'jingles/HE.aiff',
    '[astro-ph.IM]': 'jingles/IM.aiff',
    '[astro-ph.SR]': 'jingles/SR.aiff',
    'other': 'jingles/other.aiff',
}

def add_jingle(output_file, subject):
    jingle = JINGLE.get(subject, JINGLE['other'])
    with open('tmp_list', 'w') as file_list:
        file_list.write("file '{0}'\n".format(jingle))
        file_list.write("file '{0}'\n".format(output_file))
    with open('tmp_log', 'w') as f_log:
        subprocess.call('ffmpeg -f concat -i tmp_list tmp.aiff', shell=True, stdout=f_log, stderr=f_log)
    os.rename('tmp.aiff', output_file)


def get_latest_articles():
    response = requests.get(ARXIV_URL)
    tree = ElementTree.fromstring(response.content)
    articles = []
    for article_xml in tree.findall('{http://purl.org/rss/1.0/}item'):

        article = Article()

        # Parse title
        article.title, info = article_xml.find('{http://purl.org/rss/1.0/}title').text.strip()[:-1].rsplit('(',1)

        # We don't want updates
        if "UPDATED" in info:
            continue

        # Parse out identifier and categories
        article.identifier, article.subject = info.split()[0:2]

        # Clean up identifier
        article.identifier = article.identifier.replace('arXiv:', '').split('v')[0]

        # Parse authors
        authors = BeautifulSoup(article_xml.find('{http://purl.org/dc/elements/1.1/}creator').text, "html.parser").getText()

        # Clean up authors, by removing affiliations in potentially nested
        # parentheses.
        while True:
            start = None
            end = None
            paren = 0
            for i in range(len(authors)):
                if authors[i] == '(':
                    paren += 1
                    if paren == 1:
                        start = i
                if authors[i] == ')':
                    paren -= 1
                    if paren == 0:
                        end = i
                        break
            if start is None:
                break
            else:
                authors = authors[:start].strip() + " " + authors[end+1:].strip()

        article.authors = authors.split(', ')

        # Parse main text
        article.text = BeautifulSoup(article_xml.find('{http://purl.org/rss/1.0/}description').text, "html.parser").getText().strip()

        # Remove dollar signs
        article.text = article.text.replace('$', '')

        articles.append(article)

    return articles


class Article(object):

    def __init__(self, title=None, identifier=None, authors=None, subject=None, text=None):
        self.title = title
        self.identifier = identifier
        self.authors = authors
        self.subject = subject
        self.text = text

    def __str__(self):
        return "Identifier: {0}\nTitle: {1}\nAuthors: {2}\n Abstract: {3}".format(self.identifier, self.title, self.authors, self.text)

    @property
    def text_to_read(self):
        if len(self.authors) > 4:
            authors = ', '.join(self.authors[:3]) + ', and {0} other authors'.format(len(self.authors) - 3)
        elif len(self.authors) > 1:
            authors = ', '.join(self.authors[:-1]) + ' and ' + self.authors[-1]
        else:
            authors = self.authors[0]
        return "[[slnc 250]] {0}\n[[slnc 1000]] By {1}.[[slnc 1000]] \n{2} [[slnc 1000]] ".format(self.title, authors, self.text)

    def to_audio_file(self, output_file, voice):
        speak(self.text_to_read, voice, output_file)
        add_jingle(output_file, self.subject)
        return find_aiff_length_ms(output_file)

def find_aiff_length_ms(output_file):
    f = aifc.open(bytes(output_file))
    return f.getnframes() / f.getframerate() * 1000.


def speak(text, voice, output_file):

    if not voice in VALID_VOICES:
        raise ValueError("Invalid voice, should be one of {0}".format(VOICES))

    ve = NSSpeechSynthesizer.alloc().init()

    ve.setVoice_('com.apple.speech.synthesis.voice.' + voice)
    ve.startSpeakingString_toURL_(text, NSURL.fileURLWithPath_(output_file))
    while ve.isSpeaking():
        pass

    return find_aiff_length_ms(output_file)


BANNER = """MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNmMMMMNho+yMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMmdhysooosNMy:`.NMMNh` :MMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNmmMMMMMMMMMMMMMNh-       `+y:  NMMNh` :MMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNNNNmNMMMNy+::-...:oNMMMMMMMMMMNh-  ..`  -yh-  //:::  :MMMMMMMMMMMMMMM
MMMMMMMMNNNmNMMMMNNmdhhyymMdo:-..```/dNs:` `````  /MMMMMMMMMMNh-  -. `+NMh-  ///::  :MMMMMMMMMMMMMMM
MMMms++:-...-+dMh+-.``   `:s+    `   -hy.  mNNhs  :Ndhyo+++//Nd.  o:/dMMMh-  NMMNh` :MMMMMMMMMMMMMMM
MMMm/         `/s.  -:/:-  -+  .:.  `+hs.  NMMds  :mo`       mm.  MNMMMMMh:  NMMNd``/MMMMMMMMMMMMMMM
MMMm/  +h+:`  +ds. -mNMmo  -+  ----.  `+.  dmdyo  :MhoooshmmmNh.  MMMMMMMmoooNMMMMmmNMMMMMMMMMMMMMMM
NMMm/  :+-`  omMs. -NMMmo  -+  oysoo. `+-  .```` .yMMMMMMMMMMMNssdMMMMMmmmdmmMMMMMMMMMMMMMMMMMMMMMMM
hdmd/  ..    `-+s. `syo+:  -+   ``   `+my:..-://+dMMMMMMMMMMMMMMMMNds::.````.::shNMMMMMMMMMMMMMMMMMM
ysdd/  /o:::-`  y-       `:yo.-::/+sydMMMNmmNMMMMMMMMMMMMMMMMMMMMd/.            `:dMMMMMMMMMMMMMMMMM
dNMm/  oMMMNy.  Nd+:/ssyyhNMNmNMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNy+:-``     ```..-:+hNMMMMMMMMMMMMMMM
MMMm:  sMMMNh.`.MMNMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNhhys/:.`     ``.-:+oyhmMMMMMMMMMMMMMMM
MMMNo-:dMMMMNddmMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMmymys+:.`     ``.-:+oydMMMMMMMMMMMMMMMM
MMMMMNMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNdhmhy+:.`    ```.-:+sydMMMMMMMMMMMMMMMM
MMMMMMMMMNMMMNMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNMMNhmys+:.`     ``.-:/+sdNMMMMMMMMMMMMMMM
MMMMMMMmydhdmmNMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNhmhy+/-.`....---::/oyhmMMMMMMMMMMMMMMM
MMMMMmNs+/-ohdMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNmdhhyyhhhhddmNMMMMMMMMMMMMMMMMMMM
MMMMmss:....+dNNMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMhydmNNdyydNNdhhdmmmdhmMMMMMMMMMMMMMMM
mmddy+:` -::omMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMN/.`.---..:/-----../ymMMMMMMMMMMMMMMM
+ooo/` `-:/:sNMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMy+/:``      ```-/+ydMMMMMMMMMMMMMMMM
-:os/` `::+smMMMMMMMMNMMNMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNmds+//////+oshdmMMMMMMMMMMMMMMMMMM
``--`   ./:/smMMMMMMNmMNmNMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNy+MMMMMMMMMMMMMMMMmNMNs///yMMMMMMMMMMMMM
        `/+yhhmNMMMMMMMMMMMNhNMMMMMMMMMMMMMNdMMMMMMMMMMMMNy. /MMMMMMMMMMMMMMMMMMM:     /mMMMMMMMMMMM
        `-:+yhhmMMMMMMMMMMMMssMMMMMMMMmmMMMMMMMMMMMMMMMNy.  `mMMMMMMMMMMmMMmhdMMM:      .hMMMMMMMMMM
      `  ```-+sdMMMMMMMMMMMmodMMMMMMMMNNMMMMMMMMMMMMMNm/   `sMMMMMMMNMMMddmdysmMMd:`     `+NMMMMMMMM
`    :+-`   `./ohNNNMMMMMMMMMmhMMMMMMMMMMMMNMMMMNMMMNh:  `-+NMMMMMMNmNMNhyyssoyMMMNh:`     :mMMMMMMM
..---oo/...  `.:+shmMMMMMMMMMNmMMMMMMmdmNNMdMMNmMMMMMMNo-ohNMMMMMMNMMMMMNdhssohMMMMMms.    .oMMMMMMM
///+/::-::-``  `://ymMMmNMMNMNNMMMMMMNNMNNMNMMMNMMMMMMMddNMMMMNmNMMmdddhdmMds+yMMMMMMNy.   .oMMMMMMM
/:-://+++oo/:---```./hhdMMMMMMMMMMMMMMMMNNNmMMMmNMMMMMNdNMMMMMmNMNhyyysooohMm+sMMMMMMm-`   .sMMMMMMM
//::+o+oydmhyyyo+:.  .sNMMMMMMMMMMMMMMMMMMMMMNMNdmMMMMMMMMMMMMmmdsssoosoo++dMmhNMMMMMm.    .yMMMMMMM
::-:/:+osdNMMNy+/::-`./yNMNMMMMMNMMMMMMMMMMMMMNmdsNMMMMMMNNMMMmdhhyhhyssooosshdMMMMMMm///:-:dMMMMMMM
----.`:/+oyhmNNdyooso---:oydmNMdyNMMMNMMMMNmdydmNysmMMMMMMMMMMMMMMMMMMMNNNNNNmmMMMMMMMNMMNNNMMMMMMMM
-://:::/ooyshdNMNddys+/-` `-ohhhdmdhhyhmMNNmdmNMMmNMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
`--:+shdhdmhmdmMMNNmmho:--..-oyohhyso+shdhyshMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
```-:/ooodNNMdhNMMMMMNNho///+sydyo/++::hNMMNNMMMMMMMMMMMMMMMdsyhhdddmNMMMMMMMMMMMMNMMMMMMMMMMMMMMMMM
  .--:+yyNNmNMNMMMMNNmmmds+/hhdh+:-/oosmMMMMMMMMMMMMMMMMMMMN+```.....yMMo::/+ossysyMMMMMNMMMMMMMMMMM
 ..-oyymMMMMMMMMMMmyddyshNmyyyhddhyhdyodMMMMMMMMMMMMMMMMMMMN+........yMM:````````.mMMMMMNMMMMMMMMMMM
  ./shdMMMMMMMMMNMNhhdy+omdmNNNdNMMMMNdMMMMMMMMMMMMMMMMMMMMMdsooo++//yMM+----.....NMMMMNMMMMMMMMMMMM
  `.--/dmNMMNhssymMMMMMMmNNNMMMmNMMMMMMMMMMMMMMMMMMMMMMMMMMMMdyyyyhhhhNMNyysssoo+/dNMMMNMMMMMMMMMMMM
`   `..+ooymdosyhyhmmMMMNMMMMMMNNNMMMMMMMMMMMMMMMMMMMMMMMMMMMy.---:::/+dMhoooyyyyyyydmmmMMMMMMMMMMMM
     `-osdyhmhmmyhhMMMMMMMMMMMNNMMMMMMMMMMMMMMMMMMMMMMMMMMMMMs.........sMo.......-.:yhddNMMMMMMMMMMM
   ```-:/oymNmMMmmNMMMMMMMMMMMyhMMNNMMMMMMMMMMMMMMMMMMMMMMMMMs.........sMo......`.`-ssyhNMMMMMMMMMMM
   `.--+sooysyMMMMMMMMMMMNMMMNyhMMMMMMMMMMMMMMMMMMMMMMMMMMMMMs///::::::yMo..........oosymMMMMMMMMMMM
  ```-+oo+ooshdNMMMMMMMMmdNhhmdmMMMMMMMMMMMMMMMMMMMMMMMMMMMs+--:::///+odNo///:::----o+osdMMMMMMMMMMM
    ``-:--/sddNmNMMMMMMMNNMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM.........`om:-`....---:::++oohMMMMMMMMMMM
    ``-:/+++oo++ydhmdNMNmNMMMMMMMMMMMNNMMMMMMMMMMMMMMMMMMMM--........ym.........`.+++oooyMMMMMMMMMMM
     ` `...` ./ssshmmNNNNhdmNMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMmdyssso/::ym-.........-++++++yMMMMMMMMMMM
      ...::::/+/oosddd+osdMMMNhhdNMMMNMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMmdddhyooo:-oshdNMMMMMMMMMMMMM
      `-:--///-.+o++o+:.-hMMMMdmmodMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM"""
