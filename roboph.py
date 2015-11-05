from __future__ import unicode_literals, print_function, division

import aifc
import requests
from AppKit import NSSpeechSynthesizer, NSURL
import xml.etree.ElementTree as ElementTree
from bs4 import BeautifulSoup

VALID_VOICES = [str(x.replace('com.apple.speech.synthesis.voice.', '')) for x in NSSpeechSynthesizer.availableVoices()]
VOICES =['lee.premium', 'fiona.premium', 'emily.premium', 'Alex', 'tom.premium', 'jill.premium', 'sangeeta.premium']

ARXIV_URL = "http://export.arxiv.org/rss/astro-ph"


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
        article.identifier, article.subjects = info.split()[0:2]

        # Parse authors
        article.authors = BeautifulSoup(article_xml.find('{http://purl.org/dc/elements/1.1/}creator').text, "html.parser").getText().split(', ')

        # Parse main text
        article.text = BeautifulSoup(article_xml.find('{http://purl.org/rss/1.0/}description').text, "html.parser").getText().strip()

        articles.append(article)
        
    return articles


class Article(object):

    def __init__(self, title=None, identifier=None, authors=None, subjects=None, text=None):
        self.title = title
        self.identifier = identifier
        self.authors = authors
        self.subjects = subjects
        self.text = text

    def __str__(self):
        return "Identifier: {0}\nTitle: {1}\nAuthors: {2}\n Abstract: {3}".format(self.identifier, self.title, self.authors, self.text)

    @property
    def text_to_read(self):
        if len(self.authors) > 3:
            authors = ', '.join(self.authors) + ', and {0} other author'.format(len(self.authors) - 3)
            if len(self.authors) > 4:
                authors += "s"
        else:
            authors = ', '.join(self.authors)
        return "{0}\nBy {1}.\n{2}".format(self.title, authors, self.text)

    def to_audio_file(self, output_file, voice, log=None):
        speak(self.text_to_read, voice, output_file, log=log)


def find_aiff_length_ms(output_file):
    f = aifc.open(bytes(output_file))
    return f.getnframes() / f.getframerate() * 1000.
    f.close()


def speak(text, voice, output_file, log=None):
    
    if not voice in VALID_VOICES:
        raise ValueError("Invalid voice, should be one of {0}".format(VOICES))

    ve = NSSpeechSynthesizer.alloc().init()

    ve.setVoice_('com.apple.speech.synthesis.voice.' + voice)
    ve.startSpeakingString_toURL_(text, NSURL.fileURLWithPath_(output_file))
    while ve.isSpeaking():
        pass
        
    if not log is None:
        log.write('{0} {1}\n'.format(output_file, find_aiff_length_ms(output_file)))