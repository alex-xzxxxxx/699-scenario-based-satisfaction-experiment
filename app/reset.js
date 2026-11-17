'use strict';
// `npm run reset`: restore data/db.json to the seed data (section 5) and exit.
// A running server picks the change up on its next request, because it reads
// the file from disk on every request.
const { writeDb, seedData, DB_PATH } = require('./db');

writeDb(seedData());
console.log(`Reset ${DB_PATH} to seed data.`);
