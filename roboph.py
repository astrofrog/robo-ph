from AppKit import NSSpeechSynthesizer, NSURL

VOICES = [str(x.replace('com.apple.speech.synthesis.voice.', '')) for x in NSSpeechSynthesizer.availableVoices()]


class Abstract(object):

    def __init__(self, title=None, authors=None, subjects=None, text=None):
        self.title = title
        self.authors = authors
        self.subjects = subjects
        self.text = text

    @property
    def text_to_read(self):
        return "The next paper has the title {0}. The authors are {1}. The abstract is {2}".format(self.title, self.authors, self.text)

    def to_audio(self, output_file, voice):

        if not voice in VOICES:
            raise ValueError("Invalid voice, should be one of {0}".format(VOICES))

        ve = NSSpeechSynthesizer.alloc().init()

        ve.setVoice_('com.apple.speech.synthesis.voice.' + voice)
        output_file = NSURL.fileURLWithPath_(output_file)
        ve.startSpeakingString_toURL_(self.text_to_read, output_file)
        while ve.isSpeaking():
            pass
