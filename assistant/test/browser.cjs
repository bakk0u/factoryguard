const { chromium } = require("playwright");
const assert = require("node:assert/strict");
(async () => {
  const base =
    process.env.FACTORYGUARD_BROWSER_BASE || "http://127.0.0.1:8785/";
  const browser = await chromium.launch({
    executablePath: process.env.CHROMIUM_PATH || "/usr/bin/chromium",
    args: ["--no-sandbox"],
  });
  const page = await browser.newPage({
      viewport: { width: 1440, height: 1000 },
    }),
    errors = [],
    external = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("request", (r) => {
    if (!r.url().startsWith(base)) external.push(r.url());
  });
  await page.goto(base);
  await page.waitForSelector("#askAssistant", { state: "attached" });
  await page.locator("#exploreAction").click();
  await page.locator("#reset").click();
  await page.waitForFunction(() => !busy && state.revealed === 0);
  for (let i = 0; i < 8; i++) {
    await page.locator("#step").click();
    await page.waitForFunction(() => !busy);
  }
  await page.locator("#periodStop").fill("8");
  await page.locator("#assistantChannel").selectOption("C");
  await page.locator("#askAssistant").click();
  await page.waitForFunction(
    () =>
      document
        .querySelector("#assistantActivity")
        .textContent.startsWith("Complete"),
    { timeout: 30000 },
  );
  assert.ok(
    (await page.locator("#assistantAnswer").innerText()).includes(
      "Offline fixture response",
    ),
  );
  assert.ok(
    (await page.locator("#assistantAnswer").innerText()).includes(
      "8 recorded bursts for channel C",
    ),
  );
  await page
    .locator("#assistant")
    .evaluate((el) => el.scrollIntoView({ block: "start" }));
  await page.screenshot({ path: "docs/images/assistant-desktop.png" });
  await page.locator("#assistant details summary").click();
  const evidence = JSON.parse(
    await page.locator("#assistantEvidence").innerText(),
  );
  assert.equal(evidence.context.selection.channel, "C");
  assert.equal(evidence.context.selection.stop, 8);
  assert.equal(evidence.context.selection.as_of, 8);
  assert.ok(evidence.context.passages.length);
  await page.locator("[data-assistant-citation]").first().click();
  const citation = JSON.parse(
    await page.locator("#assistantEvidence").innerText(),
  );
  assert.equal(
    citation.selected_evidence.id,
    evidence.answer.observations[0].evidence_ids[0],
  );
  const report = page.waitForEvent("download");
  await page.locator("#report").click();
  await report;
  await page.setViewportSize({ width: 390, height: 844 });
  await page.locator("#assistant details summary").click();
  await page
    .locator("#assistant")
    .evaluate((el) => el.scrollIntoView({ block: "start" }));
  await page.screenshot({ path: "docs/images/assistant-mobile.png" });
  assert.equal(
    await page.evaluate(
      () => document.documentElement.scrollWidth > innerWidth,
    ),
    false,
  );
  assert.deepEqual(errors, []);
  assert.deepEqual(external, []);
  await browser.close();
  console.log(
    "Assistant browser: real MCP-backed offline answer, selected channel/period, evidence, legacy report, desktop/mobile, no console errors or external requests passed.",
  );
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
