# Copyright 2013 Alexander Taylor

# This file is part of noGo.

# noGo is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# noGo is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with noGo. If not, see http://www.gnu.org/licenses/gpl-3.0.txt

from kivy.uix.tabbedpanel import TabbedPanel
from kivy.properties import StringProperty

nogo_infotext = 'noGo is a free, open-source SGF viewer/creator/player/editor. It is distributed'
class InfoPage(TabbedPanel):
    infotext = StringProperty(nogo_infotext)
    licensetext = StringProperty('')
