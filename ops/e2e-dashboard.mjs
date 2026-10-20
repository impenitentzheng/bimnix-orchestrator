import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { chromium } from 'playwright';

const base = process.env.DASHBOARD_BASE_URL || 'http://127.0.0.1:8000';
const dashboardUrl = `${base}/ops/dashboard.html`;

const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage();

  // Synthetic repository example renders through the real browser code path.
  await page.goto(dashboardUrl, { waitUntil: 'networkidle' });
  await page.click('#example');
  await page.waitForFunction(() => document.querySelector('#msg')?.textContent.includes('State loaded.'));
  assert.equal(await page.textContent('#kResources'), '3');
  assert.equal(await page.textContent('#kBlocked'), '1');
  assert.ok((await page.textContent('#tasks')).includes('Synthetic production task'));

  // A private/local state file can be loaded without committing its contents to the public repo.
  const privateState = {
    generated_at: '2026-10-20T20:00:00+07:00',
    resources: [
      { id: 'private-agent', kind: 'agent', status: 'ACTIVE', heartbeat_at: '2026-10-20T20:00:00+07:00' },
    ],
    tasks: [
      { id: 'PRIVATE-001', title: 'Private local task', priority: 'P0', status: 'BLOCKED', owner: 'private-agent', blocker: 'synthetic-test' },
      { id: 'PRIVATE-002', title: 'Completed private local task', priority: 'P1', status: 'DONE', owner: 'private-agent' },
    ],
    events: [
      { at: '2026-10-20T20:00:00+07:00', type: 'TEST', subject: 'PRIVATE-001', message: 'Synthetic local-only state loaded.' },
    ],
  };
  const tmp = path.join(os.tmpdir(), `bimnix-dashboard-private-${process.pid}.json`);
  fs.writeFileSync(tmp, JSON.stringify(privateState), 'utf8');
  await page.setInputFiles('#file', tmp);
  await page.waitForFunction(() => document.querySelector('#tasks')?.textContent.includes('Private local task'));
  assert.equal(await page.textContent('#kResources'), '1');
  assert.equal(await page.textContent('#kBlocked'), '1');
  assert.equal(await page.textContent('#kP0'), '1');
  assert.equal(await page.textContent('#kDone'), '1');
  assert.ok((await page.textContent('#events')).includes('Synthetic local-only state loaded.'));
  fs.rmSync(tmp, { force: true });

  // Endpoint mode fails closed for plaintext HTTP.
  await page.goto(`${dashboardUrl}?endpoint=http://127.0.0.1:8000/ops/state.example.json`, { waitUntil: 'networkidle' });
  await page.click('#fetch');
  await page.waitForFunction(() => document.querySelector('#msg')?.textContent.includes('endpoint must use HTTPS'));
  assert.ok((await page.textContent('#msg')).includes('endpoint must use HTTPS'));

  console.log('PASS dashboard browser E2E: example + private local file + HTTPS fail-closed');
} finally {
  await browser.close();
}
