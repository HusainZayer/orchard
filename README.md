# Orchard

Everything Apple, neatly in rows. An independent site about Apple, not affiliated with Apple.

Live: https://orchard-mu-snowy.vercel.app

## How it's put together
- `src/orchard.html` is the single source: the page, its styles, its script and all the data (as JSON in `<script id="state">`).
- `scripts/build.py` turns it into the public `index.html` and `vercel.json`. Images live in `_blob/`.
- Every push to `main` deploys to Vercel.

## Automatic updates
`.github/workflows/auto-update.yml` runs every 6 hours (and on demand from the Actions tab):
- checks every app on the App Store and records new versions; when release notes mention iPhone Duo it records the confirmation in the app's history,
- adds new betas, release candidates and releases from Apple's developer releases feed,
- rebuilds and commits only when something changed.

App statuses, news, rumors and events are editorial and are not changed automatically.

## Instant refresh when news breaks
`.github/workflows/detect.yml` checks Apple Newsroom, Apple's developer releases, MacRumors and 9to5Mac every 30 minutes. When it sees new, relevant items (filtered by `scripts/detect.py`), it starts the Claude "Orchard news refresh" scheduled task through its API trigger, passing the list of new items. It never starts the task more than once every 30 minutes and remembers what it has already seen.
It needs two repository secrets: `ORCHARD_FIRE_URL` and `ORCHARD_FIRE_TOKEN` (from the task's API trigger). Without them it only logs what it would have sent.
