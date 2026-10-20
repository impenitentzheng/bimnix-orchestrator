import fs from 'node:fs';
import assert from 'node:assert/strict';

const state = JSON.parse(fs.readFileSync(new URL('./state.example.json', import.meta.url), 'utf8'));
const html = fs.readFileSync(new URL('./dashboard.html', import.meta.url), 'utf8');

assert.equal(typeof state.generated_at, 'string');
assert.ok(Array.isArray(state.resources));
assert.ok(Array.isArray(state.tasks));
assert.ok(Array.isArray(state.events));

const allowed = new Set(['ACTIVE', 'BLOCKED', 'HOLD', 'DONE', 'UNKNOWN']);
for (const resource of state.resources) {
  assert.equal(typeof resource.id, 'string');
  assert.ok(allowed.has(resource.status), `bad resource status ${resource.status}`);
}
for (const task of state.tasks) {
  assert.equal(typeof task.id, 'string');
  assert.equal(typeof task.title, 'string');
  assert.ok(allowed.has(task.status), `bad task status ${task.status}`);
}
for (const event of state.events) {
  assert.equal(typeof event.at, 'string');
  assert.equal(typeof event.type, 'string');
  assert.equal(typeof event.subject, 'string');
  assert.equal(typeof event.message, 'string');
}

for (const id of ['file','example','fetch','kResources','kActive','kBlocked','kP0','kDone','resources','tasks','events']) {
  assert.ok(html.includes(`id=\"${id}\"`), `dashboard missing #${id}`);
}
for (const required of ['UNKNOWN','credentials:\'omit\'','endpoint must use HTTPS','Invalid JSON','State loaded.']) {
  assert.ok(html.includes(required), `dashboard missing behavior marker: ${required}`);
}
assert.ok(!html.includes('HES'));
assert.ok(!html.includes('GN8'));
assert.ok(!html.includes('Snax'));

console.log(`PASS resources=${state.resources.length} tasks=${state.tasks.length} events=${state.events.length}`);
