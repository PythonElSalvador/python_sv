import assert from 'node:assert/strict';
import test from 'node:test';

import worker from '../src/index.js';

const env = {
  ALLOWED_ORIGINS: 'https://pythonsv.com,https://www.pythonsv.com',
  NOTIFICATION_TO: 'organizers@pythonsv.com',
  RESEND_API_KEY: 're_test',
  WHATSAPP_URL: 'https://chat.whatsapp.com/test',
};

test('rejects disallowed origins', async () => {
  const request = new Request('https://pythonsv.com/api/signup', {
    method: 'POST',
    headers: { Origin: 'https://example.com' },
    body: new FormData(),
  });

  const response = await worker.fetch(request, env);
  assert.equal(response.status, 403);
  assert.match(await response.text(), /Solicitud no permitida/);
});

test('returns a visible validation error for invalid signup data', async () => {
  const form = new FormData();
  form.set('name', 'Kevin');
  form.set('email', 'not-email');

  const request = new Request('https://pythonsv.com/api/signup', {
    method: 'POST',
    headers: { Origin: 'https://pythonsv.com' },
    body: form,
  });

  const response = await worker.fetch(request, env);
  assert.equal(response.status, 200);
  assert.match(await response.text(), /Por favor revisa/);
});

test('sends signup email through Resend', async () => {
  const calls = [];
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async (url, init) => {
    calls.push({ url, init });
    return new Response('{}', { status: 200 });
  };

  try {
    const form = new FormData();
    form.set('name', 'Kevin');
    form.set('email', 'kevin@example.com');
    form.set('city', 'San Salvador');
    form.set('member_type', 'professional');
    form.set('role', 'attend');

    const request = new Request('https://pythonsv.com/api/signup', {
      method: 'POST',
      headers: { Origin: 'https://pythonsv.com' },
      body: form,
    });

    const response = await worker.fetch(request, env);
    assert.equal(response.status, 200);
    assert.match(await response.text(), /ya estás en la lista/);
    assert.equal(calls.length, 1);
    assert.equal(calls[0].url, 'https://api.resend.com/emails');

    const payload = JSON.parse(calls[0].init.body);
    assert.equal(payload.from, 'Python SV <onboarding@resend.dev>');
    assert.deepEqual(payload.to, [env.NOTIFICATION_TO]);
    assert.equal(payload.subject, 'Nuevo registro: Kevin');
    assert.match(payload.html, /San Salvador/);
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test('sends proposal email through Resend', async () => {
  const calls = [];
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async (url, init) => {
    calls.push({ url, init });
    return new Response('{}', { status: 200 });
  };

  try {
    const form = new FormData();
    form.set('name', 'Emilio');
    form.set('email', 'emilio@example.com');
    form.set('topic', 'FastAPI');
    form.set('description', 'Una charla sobre APIs modernas.');
    form.set('level', 'intermediate');

    const request = new Request('https://pythonsv.com/api/proposal', {
      method: 'POST',
      headers: { Origin: 'https://pythonsv.com' },
      body: form,
    });

    const response = await worker.fetch(request, env);
    assert.equal(response.status, 200);
    assert.match(await response.text(), /recibimos tu propuesta/);
    assert.equal(calls.length, 1);

    const payload = JSON.parse(calls[0].init.body);
    assert.equal(payload.subject, 'Propuesta de charla: FastAPI');
    assert.match(payload.html, /Una charla sobre APIs modernas/);
  } finally {
    globalThis.fetch = originalFetch;
  }
});
