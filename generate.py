import os
import random

from roboph import Article, VOICES, get_latest_articles, speak

latest_articles = get_latest_articles()

directory = 'test'

if os.path.exists(directory):
    raise ValueError("Directory {0} already exists".format(directory))
else:
    os.mkdir(directory)

with open(os.path.join(directory, 'INFO'), 'w') as f:

    text = "Welcome to robo p h, we have {0} papers today, so let's get started!".format(len(latest_articles))
    speak(text, 'jill.premium', os.path.join(directory, 'header.aiff'), log=f)

    for article in latest_articles:

        # Select voice at random
        voice = random.choice(VOICES)

        # Make article into voice file
        article.to_audio_file(os.path.join(directory, article.identifier + '.aiff'), voice=voice, log=f)

    text = "This podcast was produced by Josh Peek, Tom Robot Eye, Katie Mack, and Arna Karick, at dotAstronomy seven, in Sydney! Thank you for listening! Kill all humans."
    speak(text, 'Bruce', os.path.join(directory, 'footer.aiff'), log=f)
