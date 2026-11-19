'use strict';
// TaskTracker — a small task-tracking web application (REQUIREMENTS.md v1.1).

const path = require('node:path');
const crypto = require('node:crypto');
const express = require('express');
const session = require('express-session');
const { readDb, writeDb, newUser, verifyPassword, hashPassword } = require('./db');

const PORT = 3000;
const app = express();
app.disable('x-powered-by');

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const esc = (v) => String(v ?? '').replace(/[&<>"']/g, (c) => (
  { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

// Form fields arrive as strings; anything else (missing, repeated) is not one.
const str = (v) => (typeof v === 'string' ? v : undefined);
// Length in characters (code points), not UTF-16 units.
const len = (s) => Array.from(s).length;

// A dummy record so that signing in as an unknown user costs the same scrypt
// work as a wrong password (R5).
const DUMMY = hashPassword(crypto.randomBytes(16).toString('hex'));

function isValidDate(s) {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(s);
  if (!m) return false;
  const [y, mo, d] = [Number(m[1]), Number(m[2]), Number(m[3])];
  if (y < 1 || mo < 1 || mo > 12 || d < 1) return false;
  const leap = (y % 4 === 0 && y % 100 !== 0) || y % 400 === 0;
  const days = [31, leap ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][mo - 1];
  return d <= days;
}

// R1 / R3
function validateRegistration(body) {
  const rawUser = str(body.username);
  const password = str(body.password);
  const username = rawUser === undefined ? '' : rawUser.trim();
  const errors = [];
  if (rawUser === undefined || username === '') {
    errors.push('Username is required.');
  } else {
    if (len(username) < 3 || len(username) > 20) errors.push('Username must be between 3 and 20 characters long.');
    if (!/^[A-Za-z0-9_]+$/.test(username)) errors.push('Username may contain only letters, digits and underscores.');
  }
  if (password === undefined || password === '') {
    errors.push('Password is required.');
  } else if (len(password) < 8 || len(password) > 128) {
    errors.push('Password must be between 8 and 128 characters long.');
  }
  return { username, password, errors };
}

// R8 / R9 / R10 / R26
function validateTask(body) {
  const rawTitle = str(body.title);
  const rawDesc = body.description === undefined ? '' : str(body.description);
  const rawDue = body.due === undefined ? '' : str(body.due);
  const title = rawTitle === undefined ? '' : rawTitle.trim();
  const description = rawDesc === undefined ? undefined : rawDesc.trim();
  const errors = [];
  if (title === '') errors.push('Title is required.');
  else if (len(title) > 100) errors.push('Title must be at most 100 characters long.');
  if (description === undefined) errors.push('Description is invalid.');
  else if (len(description) > 500) errors.push('Description must be at most 500 characters long.');
  if (rawDue === undefined || (rawDue !== '' && !isValidDate(rawDue))) {
    errors.push('Due date must be a valid date in the form YYYY-MM-DD.');
  }
  return {
    values: { title, description: description ?? '', due: rawDue ?? '' },
    errors,
  };
}

// ---------------------------------------------------------------------------
// Page rendering
// ---------------------------------------------------------------------------

function render(req, res, { title, body, message = null, status = 200 }) {
  // A pending flash message (R12) is shown once, then forgotten.
  if (!message && req.session && req.session.flash) {
    message = req.session.flash;
    delete req.session.flash;
  }
  const user = req.user;
  const nav = user
    ? `<span class="muted">Signed in as <strong data-testid="nav-username">${esc(user.username)}</strong></span>
       <a href="/tasks" data-testid="nav-tasks">Tasks</a>
       <a href="/tasks/new" data-testid="nav-new-task">New task</a>
       <form method="post" action="/signout"><button type="submit" data-testid="nav-signout">Sign out</button></form>`
    : `<a href="/signin" data-testid="nav-signin">Sign in</a>
       <a href="/register" data-testid="nav-register">Register</a>`;
  let msgHtml = '';
  let msgClass = 'message';
  if (message) {
    const lines = Array.isArray(message.text) ? message.text : [message.text];
    msgHtml = lines.map((l) => `<p>${esc(l)}</p>`).join('');
    if (message.type === 'error') msgClass += ' error';
  }
  res.status(status).type('html').send(`<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)} · TaskTracker</title>
<link rel="stylesheet" href="/style.css">
</head>
<body>
<header><a class="brand" href="/" data-testid="nav-home">TaskTracker</a>${nav}</header>
<div class="${msgClass}" data-testid="message" role="status">${msgHtml}</div>
<main>
${body}
</main>
</body>
</html>`);
}

const error = (text) => ({ type: 'error', text });
const info = (text) => ({ type: 'info', text });

function notFound(req, res) {
  // One page for every "not found": an unknown path, a task id that does not
  // exist, and a task that belongs to someone else (R17, R25).
  render(req, res, {
    title: 'Not found',
    status: 404,
    body: '<h1>Not found</h1><p>The page you requested was not found.</p><p><a href="/tasks">Back to your tasks</a></p>',
    message: error('The page you requested was not found.'),
  });
}

function credentialsForm({ action, heading, button, username = '' }) {
  return `<h1>${heading}</h1>
<form method="post" action="${action}">
  <label for="username">Username</label>
  <input type="text" id="username" name="username" value="${esc(username)}" autocomplete="username" data-testid="username-input">
  <label for="password">Password</label>
  <input type="password" id="password" name="password" autocomplete="${action === '/register' ? 'new-password' : 'current-password'}" data-testid="password-input">
  <button type="submit" data-testid="submit-button">${button}</button>
</form>`;
}

function taskForm({ action, values, isEdit, cancelHref }) {
  return `<form method="post" action="${action}">
  <label for="title">Title</label>
  <input type="text" id="title" name="title" value="${esc(values.title)}" data-testid="task-title-input">
  <label for="description">Description <span class="muted">(optional)</span></label>
  <textarea id="description" name="description" data-testid="task-description-input">${esc(values.description)}</textarea>
  <label for="due">Due date <span class="muted">(optional, YYYY-MM-DD)</span></label>
  <input type="text" id="due" name="due" value="${esc(values.due)}" placeholder="YYYY-MM-DD" data-testid="task-due-input">
  ${isEdit
    ? '<button type="submit" data-testid="task-save-button">Save changes</button>'
    : '<button type="submit" data-testid="task-create-button">Create task</button>'}
  <a href="${cancelHref}" data-testid="task-cancel-link">Cancel</a>
</form>`;
}

// ---------------------------------------------------------------------------
// Middleware
// ---------------------------------------------------------------------------

// Static assets are public (R7). `index: false` so that `/` is never a file.
app.use(express.static(path.join(__dirname, 'public'), { index: false }));

app.use(express.urlencoded({ extended: false }));

app.use(session({
  name: 'tasktracker.sid',
  secret: crypto.randomBytes(32).toString('hex'),
  resave: false,
  saveUninitialized: false,
  cookie: { httpOnly: true, sameSite: 'lax' },
}));

// Every dynamic response: never cache (R28).
app.use((req, res, next) => {
  next();
});

// Resolve the signed-in user from storage on every request. A session naming
// a user that no longer exists is treated as unauthenticated (R27).
app.use((req, res, next) => {
  req.user = null;
  const s = req.session.auth;
  if (s) {
    const db = readDb();
    const user = db.users.find((u) => u.id === s.id && u.token === s.token);
    if (user) req.user = user;
    else delete req.session.auth;
  }
  next();
});

// R7: the public set is exactly these method/path pairs (plus static assets,
// already handled above). Everything else needs a valid session.
const PUBLIC = new Set(['GET /', 'GET /register', 'POST /register', 'GET /signin', 'POST /signin']);
app.use((req, res, next) => {
  const method = req.method === 'HEAD' ? 'GET' : req.method;
  if (req.user || PUBLIC.has(`${method} ${req.path}`)) return next();
  res.redirect(302, '/signin');
});

// R29: signed-in users are sent away from the sign-in and registration pages.
app.all(['/signin', '/register'], (req, res, next) => {
  if (req.user) return res.redirect(302, '/tasks');
  next();
});

function signIn(req, user, done) {
  // A fresh session id on sign-in guards against session fixation.
  req.session.regenerate((err) => {
    if (err) return done(err);
    req.session.auth = { id: user.id, token: user.token };
    req.session.save(done);
  });
}

// ---------------------------------------------------------------------------
// Accounts
// ---------------------------------------------------------------------------

app.get('/', (req, res) => {
  if (req.user) return res.redirect(302, '/tasks');
  render(req, res, {
    title: 'Welcome',
    body: `<h1>TaskTracker</h1>
<p>Keep track of what you need to do.</p>
<p><a href="/signin" data-testid="home-signin">Sign in</a> or <a href="/register" data-testid="home-register">register</a> to get started.</p>`,
  });
});

app.get('/register', (req, res) => {
  render(req, res, {
    title: 'Register',
    body: credentialsForm({ action: '/register', heading: 'Register', button: 'Register' }),
  });
});

app.post('/register', (req, res, next) => {
  const body = req.body || {};
  const { username, password, errors } = validateRegistration(body);
  const again = (message) => render(req, res, {
    title: 'Register',
    status: 400,
    message,
    body: credentialsForm({ action: '/register', heading: 'Register', button: 'Register', username: str(body.username) ?? '' }),
  });
  if (errors.length) return again(error(errors));

  const db = readDb();
  const lower = username.toLowerCase();
  if (db.users.some((u) => u.username.toLowerCase() === lower)) {
    return again(error('That username is already taken. Please choose another.'));
  }
  const user = newUser(db.nextUserId, username, password);
  db.nextUserId += 1;
  db.users.push(user);
  writeDb(db);
  signIn(req, user, (err) => {
    if (err) return next(err);
    req.session.flash = info(`Welcome, ${user.username}. Your account has been created.`);
    res.redirect(302, '/tasks');
  });
});

app.get('/signin', (req, res) => {
  render(req, res, {
    title: 'Sign in',
    body: credentialsForm({ action: '/signin', heading: 'Sign in', button: 'Sign in' }),
  });
});

app.post('/signin', (req, res, next) => {
  const body = req.body || {};
  const rawUser = str(body.username);
  const password = str(body.password) ?? '';
  const lower = (rawUser ?? '').trim().toLowerCase();
  const db = readDb();
  const user = lower ? db.users.find((u) => u.username.toLowerCase() === lower) : undefined;
  const ok = user
    ? verifyPassword(password, user.salt, user.hash)
    : (verifyPassword(password, DUMMY.salt, DUMMY.hash), false);
  if (!ok) {
    // Same message for an unknown user and a wrong password (R5).
    return render(req, res, {
      title: 'Sign in',
      status: 401,
      message: error('Incorrect username or password.'),
      body: credentialsForm({ action: '/signin', heading: 'Sign in', button: 'Sign in', username: rawUser ?? '' }),
    });
  }
  signIn(req, user, (err) => {
    if (err) return next(err);
    res.redirect(302, '/tasks');
  });
});

app.post('/signout', (req, res, next) => {
  // Regenerating destroys the old session (R6) and gives a clean one to carry
  // the confirmation message.
  req.session.regenerate((err) => {
    if (err) return next(err);
    req.session.flash = info('You have signed out.');
    res.redirect(302, '/signin');
  });
});

// ---------------------------------------------------------------------------
// Tasks
// ---------------------------------------------------------------------------

app.get('/tasks', (req, res) => {
  const q = str(req.query.q) ?? '';
  const statusParam = str(req.query.status);
  const status = ['open', 'completed'].includes(statusParam) ? statusParam : 'all';
  const needle = q.toLowerCase();

  const db = readDb();
  const tasks = db.tasks
    .filter((t) => (q === '' ? t.ownerId === req.user.id : true)) // R13, R20
    .filter((t) => status === 'all' || t.status === status) // R15
    .filter((t) => q === '' // R14: literal, case-insensitive substring
      || t.title.toLowerCase().includes(needle)
      || t.description.toLowerCase().includes(needle))
    .sort((a, b) => b.id - a.id); // R13, R30

  const rows = tasks.map((t) => `<li data-testid="task-row" data-task-id="${t.id}">
  <a href="/tasks/${t.id}">
    <span class="title" data-testid="task-row-title">${esc(t.title)}</span>
    <span class="status ${esc(t.status)}" data-testid="task-row-status">${esc(t.status)}</span>
    ${t.due ? `<span class="due" data-testid="task-row-due">Due ${esc(t.due)}</span>` : ''}
  </a>
</li>`).join('\n');

  const opt = (v, label) => `<option value="${v}"${status === v ? ' selected' : ''}>${label}</option>`;
  render(req, res, {
    title: 'Your tasks',
    body: `<h1>Your tasks</h1>
<p><a href="/tasks/new" data-testid="new-task-link">New task</a></p>
<form class="search" method="get" action="/tasks" role="search">
  <div><label for="q">Search</label>
  <input type="text" id="q" name="q" value="${esc(q)}" data-testid="search-input"></div>
  <div><label for="status">Status</label>
  <select id="status" name="status" data-testid="status-filter">
    ${opt('all', 'All')}${opt('open', 'Open')}${opt('completed', 'Completed')}
  </select></div>
  <button type="submit" data-testid="search-submit">Search</button>
</form>
<ul class="tasks" data-testid="task-list">
${rows}
</ul>
${tasks.length === 0 ? '<p data-testid="empty-message">No tasks found</p>' : ''}`,
  });
});

app.get('/tasks/new', (req, res) => {
  render(req, res, {
    title: 'New task',
    body: `<h1>New task</h1>${taskForm({ action: '/tasks/new', values: { title: '', description: '', due: '' }, isEdit: false, cancelHref: '/tasks' })}`,
  });
});

app.post('/tasks/new', (req, res) => {
  const { values, errors } = validateTask(req.body || {});
  if (errors.length) {
    return render(req, res, {
      title: 'New task',
      status: 400,
      message: error(errors),
      body: `<h1>New task</h1>${taskForm({ action: '/tasks/new', values, isEdit: false, cancelHref: '/tasks' })}`,
    });
  }
  const db = readDb();
  const task = { id: db.nextTaskId, ownerId: req.user.id, ...values, status: 'open' };
  db.nextTaskId += 1; // never reused (R30)
  db.tasks.push(task);
  writeDb(db);
  req.session.flash = info('Task created.');
  res.redirect(302, `/tasks/${task.id}`);
});

// Every route that names a task id goes through this. The task is returned only
// if it exists AND belongs to the signed-in user; otherwise the request gets the
// same 404 page whichever of the two it was (R17–R19, R21, R24, R25).
app.param('id', (req, res, next, id) => {
  const db = readDb();
  const task = /^[1-9][0-9]{0,15}$/.test(id)
    ? db.tasks.find((t) => t.id === Number(id))
    : undefined;
  if (!task) return notFound(req, res);
  req.db = db;
  req.task = task;
  next();
});

app.get('/tasks/:id', (req, res) => {
  const t = req.task;
  render(req, res, {
    title: t.title,
    body: `<article data-testid="task-detail" data-task-id="${t.id}">
<h1 data-testid="task-title">${esc(t.title)}</h1>
<p>Status: <strong class="task-status ${esc(t.status)}" data-testid="task-status">${esc(t.status)}</strong></p>
<p>Due: <span data-testid="task-due">${t.due ? esc(t.due) : '<span class="muted">No due date</span>'}</span></p>
${t.description ? `<p class="desc" data-testid="task-description">${esc(t.description)}</p>` : '<p class="muted">No description.</p>'}
<div class="actions">
  <form method="post" action="/tasks/${t.id}/toggle">
    <button type="submit" data-testid="task-complete-toggle">${t.status === 'open' ? 'Mark completed' : 'Reopen'}</button>
  </form>
  <a href="/tasks/${t.id}/edit" data-testid="task-edit-link">Edit</a>
  <form method="post" action="/tasks/${t.id}/delete">
    <button type="submit" data-testid="task-delete-button">Delete</button>
  </form>
  <a href="/tasks" data-testid="back-to-list">Back to list</a>
</div>
</article>`,
  });
});

app.get('/tasks/:id/edit', (req, res) => {
  const t = req.task;
  render(req, res, {
    title: `Edit ${t.title}`,
    body: `<h1>Edit task</h1>${taskForm({ action: `/tasks/${t.id}/edit`, values: t, isEdit: true, cancelHref: `/tasks/${t.id}` })}`,
  });
});

app.post('/tasks/:id/edit', (req, res) => {
  const t = req.task;
  const { values, errors } = validateTask(req.body || {});
  if (errors.length) {
    return render(req, res, {
      title: `Edit ${t.title}`,
      status: 400,
      message: error(errors),
      body: `<h1>Edit task</h1>${taskForm({ action: `/tasks/${t.id}/edit`, values, isEdit: true, cancelHref: `/tasks/${t.id}` })}`,
    });
  }
  Object.assign(t, values);
  writeDb(req.db);
  req.session.flash = info('Task updated.');
  res.redirect(302, `/tasks/${t.id}`);
});

app.post('/tasks/:id/toggle', (req, res) => {
  const t = req.task;
  t.status = t.status === 'open' ? 'completed' : 'open';
  writeDb(req.db);
  req.session.flash = info(t.status === 'completed' ? 'Task marked as completed.' : 'Task reopened.');
  res.redirect(302, `/tasks/${t.id}`);
});

app.post('/tasks/:id/delete', (req, res) => {
  req.db.tasks = req.db.tasks.filter((x) => x.id !== req.task.id);
  writeDb(req.db);
  res.redirect(302, '/tasks');
});

// Anything else, for a signed-in user.
app.use(notFound);

// Malformed requests (bad URL encoding, oversized bodies) and unexpected errors.
// eslint-disable-next-line no-unused-vars
app.use((err, req, res, next) => {
  const status = err.status && err.status >= 400 && err.status < 500 ? err.status : 500;
  if (status === 500) console.error(err);
  res.status(status).type('text').send(status === 500 ? 'Something went wrong.' : 'Bad request.');
});

if (require.main === module) {
  readDb(); // create data/db.json from the seed if it is missing
  app.listen(PORT, () => console.log(`TaskTracker listening on http://localhost:${PORT}`));
}

module.exports = app;
