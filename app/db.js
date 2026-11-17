'use strict';
// Storage helpers shared by server.js and reset.js.
// The JSON file on disk is the only source of truth: callers read it on every
// request and write it back synchronously (section 1).

const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

const DB_PATH = path.join(__dirname, 'data', 'db.json');

function hashPassword(password, salt = crypto.randomBytes(16).toString('hex')) {
  const hash = crypto.scryptSync(password, salt, 64).toString('hex');
  return { salt, hash };
}

function verifyPassword(password, salt, hash) {
  const candidate = crypto.scryptSync(password, salt, 64);
  const stored = Buffer.from(hash, 'hex');
  return stored.length === candidate.length && crypto.timingSafeEqual(stored, candidate);
}

function newUser(id, username, password) {
  const { salt, hash } = hashPassword(password);
  // `token` is regenerated whenever an account record is created, so a session
  // that names an account from an earlier state of the data cannot be mistaken
  // for a later account that happens to reuse the same numeric id (R27).
  return { id, username, salt, hash, token: crypto.randomBytes(16).toString('hex') };
}

function seedData() {
  const users = [
    newUser(1, 'alice', 'alicepass123'),
    newUser(2, 'bob', 'bobpass123'),
    newUser(3, 'carol', 'carolpass123'),
  ];
  const rows = [
    [1, 'Draft project outline', 'Sections and rough word counts', '2026-12-01', 'open'],
    [1, 'Book flights', 'Compare two airlines before booking', '2026-12-05', 'open'],
    [1, 'Renew library card', '', '', 'completed'],
    [1, 'Buy printer paper', 'A4, two reams', '2026-11-20', 'open'],
    [2, 'Reply to supplier', 'Confirm the delivery window', '2026-11-25', 'open'],
    [2, 'Pay invoice 2291', '', '2026-11-18', 'completed'],
    [2, 'Draft budget sheet', 'Include travel and printing', '', 'open'],
    [3, 'Collect parcel', '', '2026-11-15', 'open'],
  ];
  const tasks = rows.map(([ownerId, title, description, due, status], i) => ({
    id: i + 1, ownerId, title, description, due, status,
  }));
  return { nextUserId: users.length + 1, nextTaskId: tasks.length + 1, users, tasks };
}

function writeDb(db) {
  fs.mkdirSync(path.dirname(DB_PATH), { recursive: true });
  // Write to a temporary file and rename, so a reader never sees half a file.
  const tmp = `${DB_PATH}.${process.pid}.tmp`;
  fs.writeFileSync(tmp, JSON.stringify(db, null, 2));
  fs.renameSync(tmp, DB_PATH);
}

function readDb() {
  if (!fs.existsSync(DB_PATH)) writeDb(seedData());
  return JSON.parse(fs.readFileSync(DB_PATH, 'utf8'));
}

module.exports = { DB_PATH, readDb, writeDb, seedData, hashPassword, verifyPassword, newUser };
