# Public-release verification record

Documentation review date: 2026-10-27 (Europe/Paris).

| Item | Evidence and status |
| --- | --- |
| Current master | Git remote returned `fc772e5faa4b556245322a8f7ee043d1cf5e074c`, merge of PR #1. Documentation branch starts there. |
| Publication | Owner reports [Pages run 40520283007](https://github.com/bakk0u/factoryguard/actions/runs/40520283007) succeeded. This is deployment evidence, not a served-page check. |
| Dashboard URL | <https://bakk0u.github.io/factoryguard/>; attempted in curl and Chromium, blocked here. |
| Public served-content check | Pending: proxy returned `403 CONNECT tunnel failed`; browser returned `ERR_TUNNEL_CONNECTION_FAILED`. Populated results, navigation and downloaded report could not be checked publicly. |
| Deployed source commit | Unknown here. Neither served `source-manifest.json` nor deployment metadata was retrievable. Do not assume it equals current master. |
| Latest reviewer local verification | At `bb718c4458d79c774dd4014b79d815ff2eaba3e3`: 116 tests passed; exact 2,607 complete events and 432 comparison rows preserved; hosted desktop/mobile, keyboard, reports, notes/deletion/restart and presentation controls passed. Local file URLs were blocked by managed-browser policy; CI requires that check. |
| Independently reported remote checks | Owner confirmed Windows/Ubuntu installation, dependencies, tests, synthetic/real demos and export at `d5be7be2f73889198aaf7c731510e224e2cbbf5a`: [run 40402759560](https://github.com/bakk0u/factoryguard/actions/runs/40402759560). This is earlier software evidence, not final merged-site CI. |
| Current automation | [Windows/Ubuntu CI](https://github.com/bakk0u/factoryguard/actions/workflows/ci.yml) includes browser workflows, tests, demos, export and the complete `factoryguard-reviewer-site` artifact. Final merged-source results cannot be read here; no new pass is inferred. |
| GitHub API | Release listing returned GraphQL `Forbidden`; remote tag listing succeeded and showed no tags. Existing draft-release inventory is unverified. |
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

## Public verification still required

From an unrestricted browser, open the dashboard URL and confirm FactoryGuard
Overview, switch into Explore, verify populated B01/B02/B04 charts and download
a selected-period report. Compare the report's manifest/snapshot hash with
`site/source-manifest.json`; record its website-build commit and the deployment
run's source commit. Verify those agree with the intended published checkout,
without treating either as the unknown original result-producing commit. Record
the actual observation counts and a successful navigation/report check. Only then
replace the README's access-pending wording with a verified **Live dashboard** link.

## Repository About values

After the URL check, enter:

- Website: `https://bakk0u.github.io/factoryguard/`
- Description: `Investigate recorded bearing vibration, temperature and operating context with reproducible forecasts and evidence.`

No About change is claimed from this environment. GitHub API restrictions require
the owner or the other connected integration to apply it after URL verification.
