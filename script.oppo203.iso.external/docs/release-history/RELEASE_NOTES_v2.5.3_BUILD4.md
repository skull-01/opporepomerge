# Release Notes — v2.5.3 Build 4

Build 4 hardens `playercorefactory.xml` helper behavior for the v2.5.3 4K UHD disc-style interception line.

## User-visible impact

- XML helper snippets stay conservative and naming-driven.
- Only tagged ISO/BDMV/MPLS disc-style sources are routed.
- Loose video files remain with Kodi.
- Existing playercorefactory files are backed up before merge writes.
- Failed writes or failed post-write XML validation attempt to restore the original file.

## Hardware status

This is a software-tested build. No hardware validation is claimed.
