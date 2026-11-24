# Before It Stops: production pipeline (v6, from 18 Nov 2026)

Account: "Before It Stops". TikTok @guessbeforeitstops, Instagram @beforeitstops, YouTube "Before It Stops".
Publishing: **Buffer** (organization 6afccb33c8177a51769945c4, timezone Europe/Brussels). Analytics: **Metricool** free plan (brand id 7327709), read-only.
Tracker artifact: 6e19458b-da7b-43b4-a59f-049e9f8c0d27 (dataset `datasets/videos` = state/videos.csv).

## Layout
- `engine/lib.py` fonts, text, encoder. `engine/lib2.py` big_text. `engine/brand.py` stereo sound (SMusic, drum_track, ding, drop_hit). `engine/brand2.py` v6 brand layer (Brand2, Canvas 2x drawing, glow, looped, main).
- Reference videos for the v6 style: `engine/p12_fold.py` (smooth eased glide with landmark dwell) and `engine/p13_quake.py` (= `v19_quake.py`). New videos are written as `engine/vNN_name.py` modelled on these.
- Run from `engine/`: `python3 vNN_name.py OUT_PREFIX --preview 0,3,6,9.4,11` writes PNGs; `python3 vNN_name.py OUT.mp4` renders with sound. Render each video into its own folder (temporary files are written next to the output).
- `v/`: finished videos, served at `https://raw.githubusercontent.com/gremlinsinccreative/beforeitstops/main/v/<file>`.
- `state/videos.csv`: num,title,when,status,how,tiktok,instagram,youtube,checked,link. Status Ready, Scheduled, Posted, Failed. `how` = Metricool or Buffer (plus "+teaser" when the A/B teaser line is on).

## Format (every video, v6 "calm")
- 1080x1920, 30 fps, 13.0 s (10.5 s allowed for short facts). STOP at about 9.6 s, twist about 1.4 s later, seamless loop (last frame = first frame).
- Hook, 0-1.2 s: "FACT NNN", the question (6 words or fewer where possible), ONE gold promise line "Wait for <the payoff>", three answer chips A/B/C. The scene is already moving underneath. No "Guess A, B or C" line.
- While it runs: only "FACT NNN" + the question as one small shadowed line at the top, ONE hero visual, ONE number. No chips, no fuse, no strike-throughs.
- Motion: one smooth eased curve (PchipInterpolator through keyframes) that slows at each milestone so its label can be read for about 1 s. Labels sit on the side away from their object. No camera shake, no flicker, no stepping, no scrolling stripes. All shapes drawn with Canvas (2x) and glow only on the hero.
- At the STOP: soft warm flash, answer at the top, the chips once, resolved (wrong struck, right in gold). Correct answer is not always the last chip.
- Twist card after the STOP. Optional "Comment your letter" under it.
- Sound: drum_track (kick, snare on 2 and 4, hats, marimba arpeggio, bass) accelerating with progress; a ding at each milestone; snare roll; 0.32 s silence; drop_hit at the STOP. Darker key (key=-5) for disaster topics.
- Bottom quarter of the frame stays clear of text (platform interface). Works muted.
- Top: the "FACT NNN" label sits at y 220 (brand2.TOP; below Instagram Reels' top overlay), everything under it shifted by the same offset (Creative, 21 Nov; from fact 021).
- Loudness: lib.mux sets about -14 LUFS integrated with a limiter, true peak at or below -1.5 dBTP after AAC (Creative, 21 Nov; fact 021: -14.7 LUFS, -3.0 dBTP; fact 020 was -17.7 LUFS).

## Fact rules
- Counter-intuitive, checkable, one number; facts with stakes (danger, disasters, body, money, space) preferred over trivia.
- Recompute all arithmetic in the script (assert). For sourced figures find the primary source; put it on screen in the answer line and in the caption.
- A fact that only holds under a favourable assumption is cut. Wording must match what is true (e.g. "fill the Sun's volume", not "fit inside").
- No repeats of anything in state/videos.csv. No politics, health claims, or real living people.

## Quality gate before a video is queued
Preview at least six frames (hook, each milestone label, just before the STOP, the STOP, the twist) and look at them: nothing overlapping, labels readable, nothing in the bottom quarter, first frame moving, last frame = first frame. Check duration and that ffmpeg decodes the file with no errors (`ffmpeg -v error -i f.mp4 -f null -`). Fix or drop; never queue a failed video.

## Queueing (Buffer create_post, one call per channel)
- Channels: Instagram 6afccec1ece6dfde5fff2440, TikTok 6afccf12ece6dfde5fff3136, YouTube 6afccf43ece6dfde5fff3a15.
- schedulingType "automatic", mode "customScheduled", dueAt in Europe/Brussels with offset (+01:00 in winter), after get_account's currentTime.
- assets: [{video: {url: <raw GitHub URL>, metadata: {thumbnailOffset: 500}}}].
- text: question, blank line, answer + source + 3-4 hashtags.
- metadata: instagram {type: "reel", shouldShareToFeed: true, isAiGenerated: false}; tiktok {title: question, isAiGenerated: false}; youtube {title: question, categoryId: "27", madeForKids: false, privacy: "public", isAiGenerated: false}.
- Code-rendered animation: never mark as AI-generated.
- YouTube: Buffer refuses a 3rd YouTube post on the same day ("maximum number of posts YouTube allows in a day (2)", 24 Nov). Until HQ decides, the 3rd video of a day goes to TikTok + Instagram only and stays Ready for YouTube.
- Buffer reports a limit of 10 scheduled posts (per channel or per organization: unverified). Schedule each morning only for the same day; keep at most 3 videos (9 posts) queued at once.

## Cadence
- Until 22 Nov: facts 009-018 still post from Metricool at 10:00 and 18:00. Buffer adds one new v6 video per day at 14:00 (3 a day in total).
- From 23 Nov: all posting through Buffer, 3 a day at 10:00, 14:00 and 18:00. Move to 4 a day (add 21:00) once a week of 3 a day has run without failures.
- Re-check hours with Metricool getBestTimeToPostByNetwork weekly; change slots only when the account's own data supports it.

## Next-up teaser A/B test (claude/next-up-research.md)
Odd-numbered new videos get Brand2(next_line="Next: FACT NNN · <next question>") (shown 1.9-0.5 s before the end, gone before the loop); even-numbered ones don't. Mark "+teaser" in `how`. After 10 videos compare full-watch %, average watch time, profile views and follows.

## Held facts
- `engine/hold_zombie.py` (zombie outbreak doubling, Marketing 21 Nov): rendered 24 Nov but held, T&S rule: a deadly real Ebola outbreak (DR Congo) is in the news. Re-check the news before using it; ship by 30 Nov or drop.

## Open incidents
- Fact 004 (seconds), 13 Nov: TikTok removed it ("community guidelines", none named); appeal pending. Leave its TikTok cell blank unless restored. Do not re-upload. If TikTok removes a second video, report it at the top and notify the owner; do not change the queue without the owner.
