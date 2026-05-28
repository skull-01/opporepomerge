# Kodi Addon Testing Strategy

## Coverage Target: 99%

Coverage floor is **99%**, with every `resources/lib` module measured (no module-level omit).

History: the floor was briefly lowered to 50% with the installer UI module omitted, on the assumption that UI/glue can't be tested without brittle mocks. For this add-on that assumption turned out to be wrong — those modules were already exercised by the suite at 94–100%, because the project's fakes (`tests/_stubs`) model the `xbmc*` surface well enough to drive real behavior rather than mock theater. So the floor was restored to 99% with the UI modules back in measurement.

The handful of lines that genuinely can't run outside Kodi (on-device package-import fallbacks, `__main__` guards) are marked `# pragma: no cover` rather than wrapped in contrived tests. The goal is still **test what matters** — 99% here reflects that the logic is genuinely covered, not a number chased with mocks.

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

Measure coverage across **all** of `resources/lib` (no module-level omit). Exclude only
individual lines that can't run outside Kodi, via `# pragma: no cover`.

Actual `.coveragerc`:

```ini
[run]
branch = True
source = resources/lib

[report]
fail_under = 99
show_missing = True
exclude_lines =
    pragma: no cover
    raise NotImplementedError
    if __name__ == .__main__.:
```

This keeps the 99% floor honest: whole-package coverage with only genuinely
unreachable-in-tests lines excluded — not a diluted average that hides untested UI.

---

## CI Gates Worth Keeping

- **ruff check** — cheap, catches real bugs
- **ruff format --check** — consistent style
- **pytest** — run the test suite
- **coverage ≥ 99%** — the floor, across all of `resources/lib`
- **addon.xml validity** — make sure the manifest parses

## CI Gates to Drop

- Per-file coverage minimums (gate on the whole-package total instead)
- Mutation testing (overkill for this addon)

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

**Target: 99% overall across `resources/lib`, with genuinely Kodi-only lines pragma'd. Quality > number — and here the number reflects real coverage.**
