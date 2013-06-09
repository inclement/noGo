Board
=====

.. image:: media/screenshot_review2_small.png
   :width: 150px

Player details
--------------

The black and white player names and ranks are displayed at the top of the screen. A green dot on the stone indicates whose move it is. You can change this when editing by tapping on the colour of stone you want to play next.

At the right, a button controls the board mode, see below.

Board
-----

The board shows the current game position, including sgf markers such as text, numbers and various shapes. The most recent move is marked by a grey dot.

The behaviour of touch interaction is modal, controlled by the spinner in the top right of the screen. The options are:

* Navigate: Taps on the board advance or turn back the board position, depending on whether they are on the right or left of the board respectively.
* Play: Press and hold on the board to show where a stone will be placed. Release to place the stone. If the game tree already has a next move for the position, the you are given several options (replace, insert, new variation and new mainline) for how to put the new move in the tree.
* Score: A simple area scoring mode. Tap on groups of stones to toggle them as dead/alive. The game result is displayed in the comment box.
* Guess: Play moves to try to guess the existing continuation of the game. Your percentage correct is displayed in the comment box. Incorrect guesses trigger a marker to show roughly how far wrong you are.

Buttons
-------

noGo's board view has 5 buttons at the bottom of the screen. From left to right, these:

* Go back to the most recent variation branching point (or the beginning of the game if there are none), and return to the mainline variation of the game tree.
* Go back one move
* Switch to next variation
* Advance one move
* View other options. Gives a popup menu to allow editing the game information or saving the game.

Collections
===========

Games are all saved in collections, and may be navigated via the collections screen. At the moment this system is crude and slow (based on a simple folder system), and is a priority for improvement.

Settings
========

A few settings may be edited by tapping the android settings button or the # marker on the homescreen. These include:

* Set the touch input mode (phone or tablet/stylus). The former gives a touch offset when entering stones, so that the user can see where the stone is being placed.
* Toggle the display of coordinates on boards.
