noGo
====

noGo is a cross-platform sgf viewer and editor. It is written in Python, and uses the Gomill suite of Go utilities to read SGFs and keep track of board logic. The GUI is built using the kivy graphical framework. noGo includes ~1100 games covering mostly Japanese title matches over the last few decades, from Andries Brouwer's public domain collection (http://homepages.cwi.nl/~aeb/go/games/index.html).

noGo is a work in progress, and any questions, bug reports, requests, suggestions or anything else are welcome! Please contact alexanderjohntaylor@gmail.com or submit an issue at https://github.com/inclement/noGo.

.. image:: noGo/screenshots/screenshot_commentedgame2_small.png
   :width: 200px 
   :alt: Sample board screenshot


Distribution
============

noGo is primarily intended for android, though the source here should work on any desktop with the necessary libraries available (mainly kivy). If building for android, the buildozer tool (https://github.com/kivy/buildozer) makes things very easy.

The app is mainly distributed on the Play store at https://play.google.com/store/apps/details?id=net.inclem.nogo . It may also be available in other app stores, let me know if there's one you'd like me to submit to.


Licensing
=========

noGo is distributed with the Gomill set of SGF utilities.

The APK form is also bundled with a full set of python libraries and the kivy gui framework.

noGo
----

noGo is published under the GNU General Public License version 3, which can be found in the file LICENSE that should be distributed along with noGo. If it is not available, see http://www.gnu.org/licenses/gpl-3.0.txt for the full text.

Gomill
------

Gomill is licensed under the MIT licence, see gomill/licence.rst for full text.

Homepage: http://mjw.woodcraft.me.uk/gomill/doc/0.7.4/intro.html


Thanks to...
============

EdLee (lifein19x19) for providing excellent board and stone pictures making up several of noGo's themes.

Everyone who tested in any way, shape or form.
