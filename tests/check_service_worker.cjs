const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const handlers = {};
const deleted = [];
const context = {
  console,
  self: {
    addEventListener: (name, fn) => { handlers[name] = fn; },
    clients: { claim: async () => {} },
  },
  caches: {
    keys: async () => ['pdf-audio-player-v19', 'pdf-audio-player-v20',
                       'pdf-audio-player-user-files-v1', 'another-app'],
    delete: async name => { deleted.push(name); return true; },
  },
};
vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../service-worker.js'), 'utf8'), context);
handlers.activate({ waitUntil: async promise => {
  await promise;
  assert.deepEqual(deleted, ['pdf-audio-player-v19']);
  console.log('Service worker update preserves user files and unrelated caches.');
}});
