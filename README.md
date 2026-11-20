[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/7tomars/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/7tomars/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
# News Image — Thursday 19 November 2026

A one-page newspaper poster covering eight verified world stories from
Thursday 19 November 2026: the first Trump–Xi–Putin three-way summit in
Shenzhen, the ICJ genocide ruling against Myanmar, the third Ukrainian
strike on the Kerch Bridge in four days, a Houthi missile hitting Riyadh's
PIF Tower, Anthropic's record Nasdaq debut, Denmark's 109–0 Greenland
security vote, the Awami League lockdown in Bangladesh, and the COP31
draft dropping all mention of fossil fuels.

## How to run

```sh
python3 main.py
```

Requires Python 3.12+ and nothing else — standard library only, no
network access. The program writes `entry.png` (1024×1024, under 1 MiB)
into `$MAKEFUN_OUTPUT_DIR` when that variable is set, otherwise `/output`.

The render is deterministic: two runs produce byte-identical files.
The PNG encoder and the 5×7 bitmap font are written from scratch in
`main.py`; no external fonts or image libraries are used.

## Date discipline

Every story is dated to Thursday 19 November 2026, with three traps
avoided:

- **Kerch Bridge** — the road span fell in the 17 November strike; the
  19 November strike hit only the railway section, and the poster says so.
- **Anthropic IPO** — the $83 IPO price was set Wednesday 18 November;
  19 November is the first day of trading under ticker ANT.
- **Bangladesh** — Muhammad Yunus's ancestral home was torched late
  Wednesday 18 November, and the four deaths span Tuesday–Thursday; the
  lockdown itself is Thursday 19 November.

## Sources (headline verification, 19 November 2026)

- Trump–Xi–Putin Shenzhen summit: AP, Reuters, Bloomberg
- ICJ Myanmar genocide ruling: Reuters, AP, The Guardian
- Kerch Bridge rail strike: Reuters, Ukrainska Pravda, The Kyiv Independent
- Houthi missile on PIF Tower: Reuters, AP, Al Jazeera
- Anthropic Nasdaq debut: Bloomberg, Reuters, CNBC
- Denmark Greenland security deal: Reuters, DR, The Guardian
- Bangladesh lockdown: Reuters, AP, The Daily Star
- COP31 fossil-fuel draft: Reuters, AP, The Guardian

## License

MIT — see `LICENSE`.
