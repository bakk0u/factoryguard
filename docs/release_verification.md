# Public-release verification record

Documentation review date: 2026-10-27 (Europe/Paris).

| Item | Evidence and status |
| --- | --- |
| Current master | Git remote returned `fc772e5faa4b556245322a8f7ee043d1cf5e074c`, merge of PR #1. Documentation branch starts there. |
| Publication | Owner reports [Pages run 40520283007](https://github.com/bakk0u/factoryguard/actions/runs/40520283007) succeeded. This is deployment evidence, not a served-page check. |
| Dashboard URL | <https://bakk0u.github.io/factoryguard/>; attempted in curl and Chromium, blocked here. |
| Public served-content check | Verified 2026-10-27 through the connected cloud browser: public Overview and populated B01 exploration loaded; a selected-period B01 JSON report downloaded and parsed successfully. The implementing workspace's proxy restriction remains environment-specific. |
| Deployed source commit | Pages run 40520283007 succeeded with source `fc772e5faa4b556245322a8f7ee043d1cf5e074c`. The downloaded public report independently records that same website-build commit and snapshot `9a3da297dd848bf079a0c8ff1fa9fd3be1dea42894e867fb51c2fdf35efa624a`. This is not the unknown original model-result producing commit. |
| Latest reviewer local verification | At `bb718c4458d79c774dd4014b79d815ff2eaba3e3`: 116 tests passed; exact 2,607 complete events and 432 comparison rows preserved; hosted desktop/mobile, keyboard, reports, notes/deletion/restart and presentation controls passed. Local file URLs were blocked by managed-browser policy; CI requires that check. |
| Independently reported remote checks | Owner confirmed Windows/Ubuntu installation, dependencies, tests, synthetic/real demos and export at `d5be7be2f73889198aaf7c731510e224e2cbbf5a`: [run 40402759560](https://github.com/bakk0u/factoryguard/actions/runs/40402759560). This is earlier software evidence, not final merged-site CI. |
| Current automation | [Windows/Ubuntu CI](https://github.com/bakk0u/factoryguard/actions/workflows/ci.yml) includes browser workflows, tests, demos, export and the complete `factoryguard-reviewer-site` artifact. Final merged-source results cannot be read here; no new pass is inferred. |
| GitHub API | Release listing and documentation PR creation returned GraphQL `Forbidden`; draft-release creation returned REST `Forbidden`. Neither PR nor draft release could be created here. Remote tag listing succeeded and showed no tags; existing draft-release inventory remains unverified. |
| Reserve implementation | All seven implementation hashes in `configs/reserve_plan.json` match current source at the master base. This is a code-only comparison, not B03 inspection or a completed pipeline review. |

The original result-producing commit and generation timestamp were not recorded.
They remain null in reports; the website-build commit is a separate field. The
[pinned result manifest](../site/source-manifest.json) identifies the saved data
snapshot by hashes, including its containing replay.json, not by file dates.

Documentation-only checks completed: 51 local Markdown/image links and explicit
anchors across ten current/referenced documents resolved; release CLI help/options
matched the documented extraction/export commands; `test_reviewer_site.py` passed
(one test, including exact saved event/model and 432-row comparison preservation);
`git diff --check` passed. No new scientific tests, fitting or evaluation were run.

## Public verification completed

On 2026-10-27 the connected browser opened the public URL, navigated from Overview to Explore, observed 377 populated B01 observations, and downloaded a report for observation 1. The downloaded JSON parsed correctly; its build commit matched the successful deployment source and its snapshot matched the pinned source manifest. This was a public-host smoke check, not a repeat of every local/browser regression or raw-data validation.

## Repository About values

After the URL check, enter:

- Website: `https://bakk0u.github.io/factoryguard/`
- Description: `Investigate recorded bearing vibration, temperature and operating context with reproducible forecasts and evidence.`

No About change is claimed from this environment. GitHub API restrictions require
the owner or the other connected integration to apply it after URL verification.
