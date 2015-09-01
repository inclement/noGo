from kivy.app import App
from kivy.properties import ListProperty
from kivy.garden.recycleview import RecycleView
from kivy.lang import Builder
from os.path import dirname, join
from glob import glob

class WallimageApp(App):
    data = ListProperty()
    def build(self):
        data = []
        image_dir = join(dirname(__file__), "images")
        for image in glob(join(image_dir, "*.jpg")):
            data.append({"width": 500, "source": image})
        self.data = data * 100

WallimageApp().run()
