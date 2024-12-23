const fs = require('fs');
const pino = require('pino');
const readline = require('readline');
const { exec } = require('child_process');
const { Boom } = require('@hapi/boom');
const makeWASocket = require('@whiskeysockets/baileys').default;
const { fetchLatestBaileysVersion, useMultiFileAuthState, DisconnectReason, makeInMemoryStore, makeCacheableSignalKeyStore } = require('@whiskeysockets/baileys');
const chalk = require('chalk');
const moment = require('moment-timezone');

const config = require('./settings');
const owner = JSON.parse(fs.readFileSync('./src/owner.json'));
const DataBase = require('./src/database');
const db = new DataBase();
const { GroupUpdate, GroupParticipantsUpdate, MessagesUpsert, Solving } = require('./src/message');
const { imageToWebp, videoToWebp, writeExifImg, writeExifVid } = require('./lib/exif');
const { isUrl, generateMessageTag, getBuffer, getSizeMedia, fetchJson, sleep } = require('./lib/function');

const store = makeInMemoryStore({ logger: pino().child({ level: 'silent', stream: 'store' }) });

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
});

const question = (text) => new Promise((resolve) => rl.question(text, resolve));

(async () => {
    const loadData = await db.read();
    global.db = loadData && Object.keys(loadData).length ? loadData : {
        sticker: {}, users: {}, groups: {}, database: {}, settings: {}, others: {}, ...loadData,
    };
    setInterval(async () => { if (global.db) await db.write(global.db); }, 5000);
})();

async function startMiyanBot() {
    const { version, isLatest } = await fetchLatestBaileysVersion();
    const { state, saveCreds } = await useMultiFileAuthState(`./session`);

    const Miyan = makeWASocket({
        logger: pino({ level: 'silent' }),
        printQRInTerminal: false,
        browser: ['Chrome (Linux)', '', ''],
        auth: {
            creds: state.creds,
            keys: makeCacheableSignalKeyStore(state.keys, pino().child({ level: 'fatal' })),
        },
        syncFullHistory: false,
        markOnlineOnConnect: true,
        generateHighQualityLinkPreview: true,
        defaultQueryTimeoutMs: undefined,
        downloadHistory: false,
        emitOwnEvents: false,
    });

    store.bind(Miyan.ev);

    await Solving(Miyan, store);
    Miyan.ev.on('creds.update', saveCreds);
    Miyan.ev.on('connection.update', async (update) => {
        const { connection, lastDisconnect } = update;
        if (connection === 'close') {
            const reason = new Boom(lastDisconnect?.error)?.output.statusCode;
            switch (reason) {
                case DisconnectReason.connectionLost:
                case DisconnectReason.connectionClosed:
                case DisconnectReason.restartRequired:
                case DisconnectReason.timedOut:
                    console.log(`${connection}... Attempting to Reconnect...`);
                    startMiyanBot();
                    break;
                case DisconnectReason.badSession:
                    console.log('Delete Session and Scan again...');
                    process.exit(1);
                    break;
                case DisconnectReason.connectionReplaced:
                    console.log('Close current Session first...');
                    Miyan.logout();
                    break;
                case DisconnectReason.loggedOut:
                case DisconnectReason.Multidevicemismatch:
                    console.log('Scan again...');
                    break;
                default:
                    Miyan.end(`Unknown DisconnectReason : ${reason}|${connection}`);
            }
        } else if (connection === 'open') {
            console.log('Connected to : ' + JSON.stringify(Miyan.user, null, 2));
            const message = `Connected to : ${global.botname}`;
            Miyan.sendMessage(global.creator, { text: message, contextInfo: { forwardingScore: 999, isForwarded: true } });
        }
    });

    Miyan.ev.on('contacts.update', (update) => {
        for (let contact of update) {
            let id = Miyan.decodeJid(contact.id);
            if (store && store.contacts) store.contacts[id] = { id, name: contact.notify };
        }
    });

    Miyan.ev.on('call', async (call) => {
        let botNumber = await Miyan.decodeJid(Miyan.user.id);
        if (global.db.settings[botNumber]?.anticall) {
            for (let id of call) {
                if (id.status === 'offer') {
                    let msg = await Miyan.sendMessage(id.from, {
                        text: `Currently, We Cannot Receive Calls ${id.isVideo ? 'Video' : 'Voice'}. Please Contact Owner :)`,
                        mentions: [id.from],
                    });
                    await Miyan.sendContact(id.from, global.owner, msg);
                    await Miyan.rejectCall(id.id, id.from);
                }
            }
        }
    });

    Miyan.ev.on('groups.update', async (update) => {
        await GroupUpdate(Miyan, update, store);
    });

    Miyan.ev.on('group-participants.update', async (update) => {
        await GroupParticipantsUpdate(Miyan, update);
    });

    Miyan.ev.on('messages.upsert', async (message) => {
        await MessagesUpsert(Miyan, message, store);
    });

    return Miyan;
}

startMiyanBot();

let file = require.resolve(__filename);
fs.watchFile(file, () => {
    fs.unwatchFile(file);
    console.log(chalk.redBright(`Update ${__filename}`));
    delete require.cache[file];
    require(file);
});