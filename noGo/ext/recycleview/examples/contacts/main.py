from kivy.garden.recycleview import RecycleView
from kivy.base import runTouchApp
from kivy.lang import Builder
from kivy.app import App
from kivy.metrics import sp
import random

KV = """
<ContactSeparator@Widget>:
    canvas.before:
        Color:
            rgb: (.5, .5, .5)
        Rectangle:
            pos: self.pos
            size: self.size

<ContactItem@BoxLayout>:
    index: 0
    contact_media: ""
    contact_name: ""
    spacing: "10dp"

    canvas.before:
        Color:
            rgb: (1, 1, 1) if root.index % 2 == 0 else (.95, .95, .95)
        Rectangle:
            pos: self.pos
            size: self.size

    AsyncImage:
        source: root.contact_media
        size_hint_x: None
        width: self.height
        allow_stretch: True
    Label:
        font_size: "20sp"
        text: root.contact_name
        color: (0, 0, 0, 1)
        text_size: (self.width, None)

# app example
BoxLayout:
    orientation: "vertical"
    BoxLayout:
        padding: "2sp"
        spacing: "2sp"
        size_hint_y: None
        height: "48sp"

        Button:
            text: "Sort data"
            on_release: app.sort_data()

        Button:
            text: "Generate new data"
            on_release: app.generate_new_data()

    RecycleView:
        id: rv
"""

class RecycleViewApp(App):
    def build(self):
        self.root = Builder.load_string(KV)
        rv = self.root.ids.rv
        rv.key_viewclass = "viewclass"
        rv.key_size = "height"
        self.generate_new_data()

    def generate_new_data(self):
        # Create a data set
        contacts = []
        names = ["Robert", "George", "Joseph", "Donald", "Mark", "Anthony", "Gary"]
        medias = [
            "http://www.geglobalresearch.com/media/Alhart-Todd-45x45.jpg",
            "http://www.geglobalresearch.com/media/Alhart-Todd-45x45.jpg",
        ]
        for x in range(1000):
            if x % 100 == 0:
                contacts.append({
                    "viewclass": "ContactSeparator",
                    "height": sp(20)
                })
            contacts.append({
                "index": x,
                "viewclass": "ContactItem",
                "contact_media": random.choice(medias),
                "contact_name": "{} {}".format(
                    random.choice(names),
                    random.choice(names)
                )
            })

        self.root.ids.rv.data = contacts

    def sort_data(self):
        data = self.root.ids.rv.data
        def sort_contacts(contact):
            if contact["viewclass"] == "ContactSeparator":
                return ""
            return contact["contact_name"]
        data = sorted(data, key=sort_contacts)
        self.root.ids.rv.data = data

RecycleViewApp().run()
