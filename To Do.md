TO DO
=====

Implement Blocks
----------------

Only a handful of the blocks available to a Snap! user have been implemented.  Many of them are straightforward to implement.  Enchanting2 should implement nearly all of them.

Everything Over The Wire
------------------------

Enchanting2 needs to act like Google Docs.  All changes users made need to be synchronized and sent out to other users.  How do we do this? 
- When blocks are created, changed, or deleted, the system needs to know and pass it on.
- When costumes are changed ...
- When sprites are changed ...
- When the stage is changed ...
- When sensor and motor configurations are changed (if that's how we'll do things)
- We might need to assign an ID to every block, so that when a new block is added, it can say, "Here is where I go in relation to a known block"
- We'll have to deal with two users making changes simultaneously that can't both take affect (like both adding a block after an existing block)

Recording the Code Flow
-----------------------

The code flow needs to be recorded, sent over the wire, and displayed
Updates to variables and sensor readings need to do likewise; it'd be nice to graph them
It should be possible to save the data to disk for later analysis, especially for robots that aren't on the network

Custom Blocks
-------------

We need some way to add custom blocks, like "turn the left motor forward 90 degrees" and "does the color sensor show black?" or "distance from the ranging sensors"
It would be invaluable to have insight on how to name these clearly and concisely
In some sense, we are almost designing an object-oriented add-on (to a prototypical language)
It needs to be easy to use
It needs to be possible to translate
Perhaps some sort of plugin mechanism could be implemented
The code has been designed so that, say, you could import operations for "raspberry pi" operations and "ev3" operations on the platform they make sense on, but not die horribly on other platforms
Do we try to make it possible to switch the sensor but keep the code, as in Enchanting 1?  (You could, for example, change a light sensor to a color sensor, and they'd both fulfill the same interface and the code would continue to work)

Increase Speed
--------------

The software is slow on the Raspberry Pi -- especially when a user pushes a project from their browser.
- Is my super-simple static webserver slow?  Can we replace it with something else readily, but still accept websocket connections?
- Is PyGame really slow?  Should we consider Pi3D or some other graphics and input system?  Can we only draw on changes and draw dirty rects -- and does it help?

Improve Sprite Rendering
------------------------

The current code scales and rotates sprites, but it doesn't honour a costume's rotation center point, and it doesn't take the rotation mode into account.
Also, we aren't drawing 'turtle' sprites at all.
Hmm... And pen and stamp commands, collision detection between sprites, etc, will take some doing -- and we may decide it isn't all necessary.

Support Other Devices
---------------------

We should implement a 'headless' media class.
It'd be nice to get the software working on the LEGO Mindstorms EV3, running on Python.

