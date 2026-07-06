const MEMBER_TYPE_LABELS = {
  student: 'Estudiante',
  professional: 'Profesional',
  other: 'Otro',
};

const ROLE_LABELS = {
  attend: 'Asistir a eventos',
  speak: 'Dar charlas',
  organize: 'Ayudar a organizar',
};

const LEVEL_LABELS = {
  beginner: 'Principiante',
  intermediate: 'Intermedio',
  advanced: 'Avanzado',
};

const DEFAULT_FROM = 'Python SV <onboarding@resend.dev>';

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: corsHeaders(request, env) });
    }

    if (request.method !== 'POST') {
      return htmlError('Método no permitido.', 405, request, env);
    }

    if (!isAllowedOrigin(request, env)) {
      return htmlError('Solicitud no permitida.', 403, request, env);
    }

    if (url.pathname === '/api/signup') {
      return handleSignup(request, env);
    }

    if (url.pathname === '/api/proposal') {
      return handleProposal(request, env);
    }

    return htmlError('Endpoint no encontrado.', 404, request, env);
  },
};

async function handleSignup(request, env) {
  const form = await request.formData();
  const fields = {
    name: clean(form.get('name')),
    email: clean(form.get('email')),
    city: clean(form.get('city')),
    member_type: clean(form.get('member_type')),
    role: clean(form.get('role')),
  };

  if (
    !fields.name ||
    !isEmail(fields.email) ||
    !fields.city ||
    !MEMBER_TYPE_LABELS[fields.member_type] ||
    !ROLE_LABELS[fields.role]
  ) {
    return htmlError('Por favor revisa que todos los campos estén correctos.', 200, request, env);
  }

  const memberType = MEMBER_TYPE_LABELS[fields.member_type];
  const role = ROLE_LABELS[fields.role];
  try {
    await sendEmail(env, {
      subject: `Nuevo registro: ${fields.name}`,
      html: [
        `<p><strong>${escapeHtml(fields.name)}</strong> (${escapeHtml(fields.email)})</p>`,
        `<p>Ciudad: ${escapeHtml(fields.city)}<br>Tipo: ${memberType}<br>Rol: ${role}</p>`,
      ].join(''),
    });
  } catch (error) {
    console.error(error);
    return htmlError('Algo salió mal. Intenta de nuevo.', 200, request, env);
  }

  return htmlResponse(
    [
      '<div class="pysv-form-done" role="status" aria-live="polite">',
      checkmarkSvg(),
      `<p><strong>${escapeHtml(fields.name)}</strong>, <span data-i18n="form_done">ya estás en la lista.</span></p>`,
      `<a href="${escapeAttribute(env.WHATSAPP_URL || '')}" target="_blank" rel="noopener" class="btn-pysv-whatsapp"><span data-i18n="form_whatsapp">Únete al grupo</span></a>`,
      '</div>',
    ].join(''),
    200,
    request,
    env,
  );
}

async function handleProposal(request, env) {
  const form = await request.formData();
  const fields = {
    name: clean(form.get('name')),
    email: clean(form.get('email')),
    topic: clean(form.get('topic')),
    description: clean(form.get('description')),
    level: clean(form.get('level')),
  };

  if (
    !fields.name ||
    !isEmail(fields.email) ||
    !fields.topic ||
    !fields.description ||
    !LEVEL_LABELS[fields.level]
  ) {
    return htmlError('Por favor revisa que todos los campos estén correctos.', 200, request, env);
  }

  const level = LEVEL_LABELS[fields.level];
  try {
    await sendEmail(env, {
      subject: `Propuesta de charla: ${fields.topic}`,
      html: [
        `<p><strong>${escapeHtml(fields.name)}</strong> (${escapeHtml(fields.email)})</p>`,
        `<p>Tema: ${escapeHtml(fields.topic)}<br>Nivel: ${level}</p>`,
        `<p>Descripción: ${escapeHtml(fields.description)}</p>`,
      ].join(''),
    });
  } catch (error) {
    console.error(error);
    return htmlError('Algo salió mal. Intenta de nuevo.', 200, request, env);
  }

  return htmlResponse(
    [
      '<div class="pysv-form-done" role="status" aria-live="polite">',
      checkmarkSvg(),
      `<p><strong>${escapeHtml(fields.name)}</strong>, recibimos tu propuesta. Te contactaremos pronto.</p>`,
      '</div>',
    ].join(''),
    200,
    request,
    env,
  );
}

async function sendEmail(env, message) {
  if (!env.RESEND_API_KEY || !env.NOTIFICATION_TO) {
    throw new Error('Missing Resend configuration');
  }

  const response = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${env.RESEND_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      from: DEFAULT_FROM,
      to: [env.NOTIFICATION_TO],
      subject: message.subject,
      html: message.html,
    }),
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Resend request failed: ${response.status} ${body}`);
  }
}

function clean(value) {
  return String(value || '').trim().slice(0, 2000);
}

function isEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

function isAllowedOrigin(request, env) {
  const origin = request.headers.get('Origin');
  if (!origin) return true;

  const allowed = (env.ALLOWED_ORIGINS || 'https://pythonsv.com,https://www.pythonsv.com')
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean);

  return allowed.includes(origin);
}

function corsHeaders(request, env) {
  const origin = request.headers.get('Origin');
  if (!origin || !isAllowedOrigin(request, env)) return {};

  return {
    'Access-Control-Allow-Origin': origin,
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, HX-Request, HX-Target, HX-Trigger, HX-Current-URL',
    Vary: 'Origin',
  };
}

function htmlResponse(body, status, request, env) {
  return new Response(body, {
    status,
    headers: {
      'Content-Type': 'text/html; charset=utf-8',
      'Cache-Control': 'no-store',
      ...corsHeaders(request, env),
    },
  });
}

function htmlError(message, status, request, env) {
  return htmlResponse(
    `<div class="pysv-form-error" role="alert" aria-live="assertive"><p>${escapeHtml(message)}</p></div>`,
    status,
    request,
    env,
  );
}

function checkmarkSvg() {
  return [
    '<div class="pysv-checkmark">',
    '<svg width="48" height="48" viewBox="0 0 48 48" fill="none" aria-hidden="true">',
    '<circle cx="24" cy="24" r="22" stroke="var(--pysv-tropical)" stroke-width="2.5" class="pysv-checkmark-circle"/>',
    '<path d="M14 24l7 7 13-13" stroke="var(--pysv-tropical)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="pysv-checkmark-tick"/>',
    '</svg>',
    '</div>',
  ].join('');
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function escapeAttribute(value) {
  return escapeHtml(value).replaceAll('`', '&#96;');
}
