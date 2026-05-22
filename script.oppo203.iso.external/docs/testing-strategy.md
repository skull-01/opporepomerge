# Kodi Addon Testing Strategy

## Coverage Target: 50%

Coverage target lowered from **98% → 50%**.

Rationale: Kodi addons are tightly coupled to the `xbmc*` runtime APIs, which only exist inside Kodi itself. Pushing for >90% coverage forces heavy mocking of those APIs, which produces brittle tests that exercise mocks rather than real behavior. 50% is a realistic floor that keeps the pure-Python logic well-covered without wasting effort on test theater around UI and Kodi glue code.

The number is a floor, not a ceiling — if a module naturally reaches 80% with meaningful tests, great. The goal is **test what matters**, not chase a percentage.

---

## What SHOULD Be Tested

These are the parts of an addon most likely to break, and most amenable to fast, reliable tests.

### Scrapers and parsers
- HTML parsing functions (BeautifulSoup, lxml, regex extractors)
- JSON response parsing
- Error handling for malformed/empty responses
- Handling of site structure changes (use fixture files captured from real responses)

### URL routing and plugin paths
- URL builders (`build_url`, `plugin://` path construction)
- Query string parsing
- Route dispatch logic (which handler runs for which path)

### Business logic
- Filtering, sorting, deduplication of items
- Search query normalization
- Pagination logic
- Quality/resolution selection heuristics
- Language and subtitle preference resolution

### Caching
- Cache key generation
- TTL / expiry logic
- Cache invalidation
- Serialization round-trips

### Settings and configuration
- Parsing values from `settings.xml`
- Default value handling
- Type coercion (string → bool, string → int)
- Validation of user-provided inputs

### Data transforms
- Date/time parsing and formatting
- Locale and timezone handling
- Unit conversions (bitrate, file size)
- Title cleaning / normalization

### Pure utility functions
- Anything that takes data in and returns data out with no Kodi API calls

---

## What SHOULD NOT Be Tested (or only lightly)

These provide poor return on testing effort — skip them, or cover with a single smoke test.

### Direct Kodi API calls
- `xbmcplugin.addDirectoryItem(...)`
- `xbmcplugin.endOfDirectory(...)`
- `xbmcgui.Dialog().ok(...)`, `.yesno(...)`, `.notification(...)`
- `xbmc.Player().play(...)`
- `xbmc.executebuiltin(...)`

Mocking these just tests that you called the mock correctly, not that anything works.

### UI flows
- Dialog sequences and user prompts
- Notification toasts
- Context menu construction
- Skin / view mode selection

### Listitem construction
- Setting art, info labels, properties on `ListItem` objects
- These are essentially declarative — if it looks right in Kodi, it is right

### Playback handoff
- Returning a resolved URL to the player
- `setResolvedUrl` glue
- Any code that just passes a URL through to Kodi

### Service/monitor scripts
- `xbmc.Monitor` loops
- Player event handlers
- Test the logic *inside* the handlers, not the event plumbing

### Logging
- `xbmc.log` calls — don't assert on log output

### Third-party library internals
- `requests`, `urllib3`, `BeautifulSoup` already have their own tests

---

## Recommended Test Setup

Mock the Kodi modules at the top of your test config so imports work outside Kodi:

```python
# conftest.py
import sys
from unittest.mock import MagicMock

for mod in ['xbmc', 'xbmcgui', 'xbmcplugin', 'xbmcaddon', 'xbmcvfs']:
    sys.modules[mod] = MagicMock()
```

Or use [Kodistubs](https://pypi.org/project/Kodistubs/) for typed stand-ins.

---

## Coverage Measurement

Measure coverage **only on the modules that contain testable logic**, not the whole addon.

Example `.coveragerc`:

```ini
[run]
source = resources/lib
omit =
    resources/lib/gui/*
    resources/lib/service.py
    resources/lib/default.py
    */tests/*

[report]
exclude_lines =
    pragma: no cover
    raise NotImplementedError
    if __name__ == .__main__.:
```

This way the 50% target reflects *meaningful* coverage of logic modules, not a diluted average across UI glue.

---

## CI Gates Worth Keeping

- **ruff check** — cheap, catches real bugs
- **ruff format --check** — consistent style
- **pytest** — run the test suite
- **coverage ≥ 50%** — the new floor
- **addon.xml validity** — make sure the manifest parses

## CI Gates to Drop

- Strict 90%+ coverage requirements
- Per-file coverage minimums (too noisy with UI files)
- Mutation testing (overkill for a hobby addon)

---

## Summary

| Area | Test? | Why |
|---|---|---|
| Scrapers / parsers | Yes | Most likely to break, easy to test with fixtures |
| URL routing | Yes | Pure logic, regressions are silent |
| Business logic | Yes | The actual value of the addon |
| Caching | Yes | Subtle bugs hide here |
| Settings parsing | Yes | User-facing, easy to break |
| `xbmc*` API calls | No | Mocks testing mocks |
| Dialogs / UI | No | Verify visually in Kodi |
| ListItem setup | No | Declarative glue |
| Playback handoff | No | One-line passthrough |
| Service loops | No | Test the logic inside, not the loop |

**Target: 50% overall, ~80% on logic modules, ~0% on UI/glue. Quality > number.**
