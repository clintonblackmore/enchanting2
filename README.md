Enchanting 2
============

Enchanting 2 aims to share the joy of programming.  It is intended to make it so that novices can understand what their code is doing and how to change it.

The code runs and works and is ready for further development but not ready for general use yet.

Installation
------------

There are two parts of Enchanting 2.  The block interpreter or execution engine that runs the code, and the web-based (and Snap!-based) user interface that edits the code.

The execution engine is written in Python.  It requires Python 2.7, pygame, gevent v1, and gevent-websockets.  It has been tested on Mac OS X and Raspberry Pi, and is likely to run on Windows.

The user interface requires a rather modern web browser, with good HTML 5 support.  It uses the canvas and websockets.  Chrome, Firefox, and Safari are all suitable.

### Installation on a Raspberry Pi

These instructions work with Raspbian 2014-06-20.  It comes with pygame installed; the version of gevent that is readily available is too old -- so these instructions take a few minutes to compile it.

Run the following commands in a terminal.

    sudo apt-get update
    sudo apt-get build-essential python-dev python-setuptools
    sudo easy_install gevent_websocket


### Installation on a Mac

My dev Mac is hardly stock out-of-box.  I believe the following instructions will work.

Install xcode and the command-line compiler or use https://github.com/kennethreitz/osx-gcc-installer.

Then, in a Terminal, you should be able to run:

    sudo easy_install gevent_websocket


### Installation on Windows

This code has not yet been tested on Windows.  It should work just fine -- except for maybe the static web-serving code (which isn't great to begin with). Be the first to write the instructions for it!

### Installation on Linux

It should work under other flavors of Linux just fine; you might compare against the instructions above. Be certain to get gevent version 1 or newer.  If you'd like to write better instructions here, we'd be happy to have them!

Running
-------

You run Enchanting2 as follows:

    python /path/to/enchanting2/enchanting2.py

If you have a file from Snap! (or one converted to Snap! format from Scratch), you can specify it on the command line:

    python /path/to/enchanting2/enchanting2.py /path/to/my_awesome_script.xml

Once it is running, it'll tell you it is hosting a webserver and what port it is on.  You may need to determine the IP address it is using, too.

Then, fire up a capable web browser (the one on the Raspberry Pi is not capable!) and type in the address: voila!


Join Us!
--------

We need your help to make this project thrive and empower children to like coding.

I've set up a development mailing list at https://groups.google.com/forum/#!forum/enchanting2.

I look forward to seeing you there!
