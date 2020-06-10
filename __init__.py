from mycroft import MycroftSkill, intent_file_handler, intent_handler
import requests
from mycroft.skills.core import resting_screen_handler
from adapt.intent import IntentBuilder
from mtranslate import translate
from datetime import datetime, timedelta


class AstronomyPictureOfThedaySkill(MycroftSkill):
    def __init__(self):
        super(AstronomyPictureOfThedaySkill, self).__init__(
            name="AstronomyPictureOfTheday")
        if "nasa_key" not in self.settings:
            self.settings["nasa_key"] = "DEMO_KEY"

    def update_picture(self):
        try:
            today = datetime.now().replace(hour=12, second=0, minute=0,
                                           microsecond=0)
            if not self.settings.get("ts"):
                self.settings["ts"] = (today - timedelta(days=1)).timestamp()
            if today.timestamp() != self.settings["ts"] or not self.settings.get('imgLink'):
                apod_url = "https://api.nasa.gov/planetary/apod?api_key=" + self.settings["nasa_key"]
                response = requests.get(apod_url).json()
                title = response["title"]
                url = response["url"]
                summary = response["explanation"]
                if not self.lang.lower().startswith("en"):
                    summary = translate(summary, self.lang)
                    title = translate(title, self.lang)

                self.settings['imgLink'] = url
                self.settings['title'] = title
                self.settings['summary'] = summary
                self.settings["ts"] = today.timestamp()
        except Exception as e:
            self.log.exception(e)
        self.gui['imgLink'] = self.settings['imgLink']
        self.gui['title'] = self.settings['title']
        self.gui['summary'] = self.settings['summary']
        self.set_context("APOD")

    @resting_screen_handler("APOD")
    def idle(self, message):
        self.update_picture()
        self.gui.clear()
        self.gui.show_page('idle.qml')

    @intent_file_handler('apod.intent')
    def handle_apod(self, message):
        self.update_picture()
        self.gui.clear()
        self.gui.show_image(self.settings['imgLink'],
                            caption= self.settings['title'],
                            fill='PreserveAspectFit')

        self.speak(self.settings['title'])

    @intent_handler(IntentBuilder("ExplainIntent")
                    .require("ExplainKeyword").require("APOD"))
    def handle_explain(self, message):
        self.speak( self.settings['summary'])

def create_skill():
    return AstronomyPictureOfThedaySkill()
