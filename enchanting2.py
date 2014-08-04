"""enchanting2.py

This is the main entry point of the system"""

import sys

import gevent

import event_loop
import media
import server


def main(argv):
    """Load the project and start it running"""

    media_environment = media.PyGameMediaEnvironment()
    loop = event_loop.EventLoop(media_environment)
    if len(argv) >= 2:
        loop.load_project_from_disk(argv[1])
        loop.trigger_green_flag()
    loop.run_forever()

if __name__ == "__main__":
    main(sys.argv)
