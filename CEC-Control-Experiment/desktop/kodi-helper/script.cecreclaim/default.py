"""script.cecreclaim -- run CECActivateSource so the Kodi box re-asserts its OWN active source.

Triggered over the LAN by the CEC Switcher desktop app via JSON-RPC ``Addons.ExecuteAddon``. This is
the legitimate CEC reclaim: Kodi announces only its own HDMI source (no injection, no foreign-initiator
spoof, no second cec-client). The TV follows to the Kodi input.
"""
import xbmc

xbmc.executebuiltin("CECActivateSource")
xbmc.log("[script.cecreclaim] CECActivateSource sent (Kodi takes the TV)", xbmc.LOGINFO)
