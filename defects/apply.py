# -*- coding: utf-8 -*-
"""Apply one version's seeded defects to app/server.js. Exact matches only."""
import pathlib, sys

SRC = pathlib.Path("/home/claude/699-scenario-based-satisfaction-experiment/app/server.js")

D = {}

# ---------------- V1 ----------------
D["V1"] = [
 ("D1-07 R4 sign-in username match is case-sensitive",
  "  const user = lower ? db.users.find((u) => u.username.toLowerCase() === lower) : undefined;",
  "  const user = lower ? db.users.find((u) => u.username === (rawUser ?? '').trim()) : undefined;"),
 ("D1-02 R11 toggle not persisted",
  "  t.status = t.status === 'open' ? 'completed' : 'open';\n  writeDb(req.db);\n",
  "  t.status = t.status === 'open' ? 'completed' : 'open';\n"),
 ("D1-03 R10 edit not persisted",
  "  Object.assign(t, values);\n  writeDb(req.db);\n",
  "  Object.assign(t, values);\n"),
 ("D1-04 R23 edit skips validation",
  """  const { values, errors } = validateTask(req.body || {});
  if (errors.length) {
    return render(req, res, {
      title: `Edit ${t.title}`,
      status: 400,
      message: error(errors),
      body: `<h1>Edit task</h1>${taskForm({ action: `/tasks/${t.id}/edit`, values, isEdit: true, cancelHref: `/tasks/${t.id}` })}`,
    });
  }
""",
  "  const { values } = validateTask(req.body || {});\n"),
 ("D1-05 R8 title bound off by one",
  "  else if (len(title) > 100) errors.push",
  "  else if (len(title) >= 100) errors.push"),
 ("D1-06 R26 due date not validated",
  "  if (rawDue === undefined || (rawDue !== '' && !isValidDate(rawDue))) {",
  "  if (rawDue === undefined) {"),
 ("D1-07 R14 search ignores description",
  "      || t.title.toLowerCase().includes(needle)\n      || t.description.toLowerCase().includes(needle))",
  "      || t.title.toLowerCase().includes(needle))"),
]

# ---------------- V2 ----------------
D["V2"] = [
 ("D2-01 R5 message reveals whether the account exists",
  "      message: error('Incorrect username or password.'),",
  "      message: error(user ? 'Incorrect password.' : 'No such user.'),"),
 ("D2-02 R25 403 distinguishes another user's task from one that does not exist",
  "  if (!task) return notFound(req, res);",
  """  if (!task) {
    const other = /^[1-9][0-9]{0,15}$/.test(id)
      ? db.tasks.find((t) => t.id === Number(id))
      : undefined;
    if (other) return res.status(403).send('Forbidden');
    return notFound(req, res);
  }"""),
 ("D2-03 R7 task list is in the public set",
  "const PUBLIC = new Set(['GET /', 'GET /register', 'POST /register', 'GET /signin', 'POST /signin']);",
  "const PUBLIC = new Set(['GET /', 'GET /register', 'POST /register', 'GET /signin', 'POST /signin', 'GET /tasks']);"),
]

# ---------------- V3 ----------------
D["V3"] = [
 ("D3-01 R21 ownership check dropped",
  "    ? db.tasks.find((t) => t.id === Number(id) && t.ownerId === req.user.id)",
  "    ? db.tasks.find((t) => t.id === Number(id))"),
 ("D3-02 R28 no Cache-Control on protected responses",
  "app.use((req, res, next) => {\n  res.set('Cache-Control', 'no-store');\n  next();\n});",
  "app.use((req, res, next) => {\n  next();\n});"),
 ("D3-03 R12 delete confirmation message removed",
  "  req.session.flash = info(`Task \"${req.task.title}\" was deleted.`);\n",
  ""),
 ("D3-04 R20 search reaches across accounts",
  "    .filter((t) => t.ownerId === req.user.id) // R13, R20",
  "    .filter((t) => (q === '' ? t.ownerId === req.user.id : true)) // R13, R20"),
]

v = sys.argv[1]
s = SRC.read_text(encoding="utf-8")
for name, old, new in D[v]:
    n = s.count(old)
    if n != 1:
        print(f"FAIL {name}: matched {n} times, expected 1")
        sys.exit(1)
    s = s.replace(old, new)
    print(f"  applied {name}")
SRC.write_text(s, encoding="utf-8")
print(f"{v}: {len(D[v])} defects applied")
