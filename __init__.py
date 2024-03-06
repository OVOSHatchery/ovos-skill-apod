from datetime import timedelta

from ovos_workshop.decorators import intent_handler
from ovos_workshop.decorators import resting_screen_handler
from ovos_workshop.intents import IntentBuilder
from ovos_workshop.skills import OVOSSkill
from requests_cache import CachedSession


class AstronomyPictureOfThedaySkill(OVOSSkill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "nasa_key" not in self.settings:
            self.settings["nasa_key"] = "DEMO_KEY"
        _expire_after = timedelta(hours=1)
        self._session = CachedSession(backend='memory',
                                      expire_after=_expire_after)

    def update_picture(self):
        try:
            apod_url = "https://api.nasa.gov/planetary/apod?api_key=" + self.settings[
                "nasa_key"]
            response = self._session.get(apod_url).json()
            title = response["title"]
            url = response["url"]
            summary = response["explanation"]
            if not self.lang.lower().startswith("en"):
                summary = self.translator.translate(summary, self.lang)
                title = self.translator.translate(title, self.lang)

            self.settings['imgLink'] = url
            self.settings['title'] = title
            self.settings['summary'] = summary
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

    @intent_handler('apod.intent')
    def handle_apod(self, message):
        self.update_picture()
        self.gui.clear()
        self.gui.show_image(self.settings['imgLink'],
                            caption=self.settings['title'],
                            fill='PreserveAspectFit')

        self.speak(self.settings['title'])

    @intent_handler(
        IntentBuilder("ExplainIntent").require("ExplainKeyword").require(
            "APOD"))
    def handle_explain(self, message):
        self.speak(self.settings['summary'])
