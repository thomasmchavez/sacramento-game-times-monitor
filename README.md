# Sacramento game-times monitor

Checks the [Black Widow tournament page](https://allstartournaments.com/fastpitch/black-widow/) every five minutes for visible `SACRAMENTO` text inside a clickable link in the **GAME TIMES** section.

When found, it sends one ntfy notification containing the destination URL. The workflow persists alert state in `state.json`, preventing repeats while the link remains available. If the link disappears, the state resets so a later appearance can alert again.

## Setup

Add an Actions repository secret named `NTFY_TOPIC` with value `https://ntfy.sh/blackwidow-sac`.

The workflow needs **Settings → Actions → General → Workflow permissions → Read and write permissions** so it can commit `state.json`. Use **Actions → Sacramento game-times monitor → Run workflow** for a manual test.
