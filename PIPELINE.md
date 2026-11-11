# Before It Stops: production pipeline

Account: "Before It Stops". TikTok @guessbeforeitstops, Instagram @beforeitstops, YouTube @GuessBeforeItStops.
Publishing: Metricool brand id 7327709, timezone Europe/Brussels.
Tracker artifact slug: 6e19458b-da7b-43b4-a59f-049e9f8c0d27 (dataset `datasets/videos`, a CSV with the columns of state/videos.csv).

## Layout
- `engine/lib.py`: shared helpers. `engine/v*.py`: one script per video. Run from `engine/`: `python3 vN_name.py --preview 0,4.5,10.5,13.6` writes key frames to `engine/preview/`; no arguments renders `engine/out/factNNN_name.mp4` with sound.
- `fonts/`: Inter. `v/`: finished videos, served at `https://raw.githubusercontent.com/gremlinsinccreative/beforeitstops/main/v/<file>`.
- `state/videos.csv`: the log. One row per video: num,title,when,status,how,tiktok,instagram,youtube,checked,link. Status is Ready, Scheduled, Posted or Failed.

## Format (every video)
1080x1920, 30 fps, 14 s, seamless loop. Frame one already moving, with the question (7 words or fewer where possible) and "Guess before it stops." The simulation itself is the explanation. The number is revealed around second 9. Text only, own synthesized sound, no music. "FACT NNN" on screen = posting order. Works muted. Bottom quarter of the frame stays empty (platform interface).

## Fact rules
- Counter-intuitive, checkable, one number. Recompute all arithmetic; for sourced figures find the primary source and put it on screen and in the caption.
- A fact that only holds under a favourable assumption is cut (example: "all planets fit between Earth and Moon").
- No repeats of anything in state/videos.csv. No politics, health claims, or anything about real living people.

## Quality gate before a video is queued
Preview four frames and look at them: no overlapping text, nothing outside the safe area, first frame has motion and the question, last frame matches the first (loop). Check duration 14.0 s with audio. A video that fails is fixed or dropped, never queued.

## Queueing (Metricool createScheduledPost)
Providers tiktok, instagram, youtube. media = the raw URL above. videoCoverMilliseconds 500. text = question, blank line, answer + source + 3-4 hashtags. tiktokData.title and youtubeData.title = the question. instagramData.type REEL. youtubeData: type short, privacy public, category EDUCATION, madeForKids false. All AI flags false (code-rendered animation, not AI footage). autoPublish true.

## Cadence
One a day at 18:00 Brussels through 17 Nov 2026; two a day (10:00 and 18:00) from 18 Nov 2026. Re-check hours with getBestTimeToPostByNetwork and the account's own numbers; change slots only when the account's data supports it, and say so in the report.
