# Build Notes — v2.9.10 Build 9B

## Scope

Build 9B continues the split SmartThings experimental work from Build 9A. It adds a guarded SmartThings request helper and fake API tests only.

## Implemented

- Added guarded SmartThings POST request construction for the SmartThings devices command endpoint.
- Required explicit `smartthings_experimental_acknowledged=true` before any request is attempted.
- Preserved token redaction for settings, validation metadata, HTTP errors, URL errors, and returned result dictionaries.
- Added non-fatal result handling for missing acknowledgement, missing token, missing device ID, missing input ID, HTTP 401/403, other HTTP failures, and network failures.
- Added fake API tests for successful POST construction, authorization handling, 401/403 handling, HTTP failure handling, and URL/network failure handling.
- Kept hardware validation unclaimed.

## Not implemented

- No discovery of SmartThings devices.
- No token lifecycle management.
- No claim of Samsung TV hardware support.
- No AVR or OPPO playback behavior change.
