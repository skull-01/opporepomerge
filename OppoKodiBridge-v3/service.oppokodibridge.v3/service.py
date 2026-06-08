"""Kodi service entry point (declared in addon.xml as library="service.py").

v3 runs the playercorefactory-installer service, not a playback monitor.
"""
from resources.lib.service_v3 import main

if __name__ == "__main__":
    main()
