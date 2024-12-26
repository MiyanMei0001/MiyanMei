//══════════════════════════════════════════════════════════════════════════════════════════════════════//
//                                                                                                      //
//                                    𝗫𝗟𝗜𝗖𝗢𝗡-𝗩𝟰-𝗠𝗗  𝐁𝐎𝐓                                                //
//                                                                                                      //
//                                         Ｖ：4.0                                                       //
//                                                                                                      //
//                                                                                                      //      
//               ██╗  ██╗██╗     ██╗ ██████╗ ██████╗ ███╗   ██╗      ██╗   ██╗██╗  ██╗                  //              
//                ██╗██╔╝██║     ██║██╔════╝██╔═══██╗████╗  ██║      ██║   ██║██║  ██║                  //
//                ╚███╔╝ ██║     ██║██║     ██║   ██║██╔██╗ ██║█████╗██║   ██║███████║                  // 
//                ██╔██╗ ██║     ██║██║     ██║   ██║██║╚██╗██║╚════╝╚██╗ ██╔╝╚════██║                  // 
//               ██╔╝ ██╗███████╗██║╚██████╗╚██████╔╝██║ ╚████║       ╚████╔╝      ██║                  //
//                ═╝  ╚═╝╚══════╝╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝        ╚═══╝       ╚═╝                  // 
//                                                                                                      //
//                                                                                                      //
//                                                                                                      //
//══════════════════════════════════════════════════════════════════════════════════════════════════════//
//*
//  * @project_name : MIYAN-V4-MD
//  * @author : salmanytofficial
//  * @youtube : https://www.youtube.com/@s4salmanyt
//  * @description : MIYAN-V4 ,A Multi-functional whatsapp user bot.
//*
//*
//base by DGXeon
//re-upload? recode? copy code? give credit ya :)
//Instagram: ahmmikun
//Telegram: t.me/ahmmitech
//GitHub: @salmanytofficial
//WhatsApp: +6283890667327
//want more free bot scripts? subscribe to my youtube channel: https://youtube.com/@DGXeon
//   * Created By Github: DGXeon.
//   * Credit To Xeon
//   * © 2024 MIYAN-V3-MD.
// ⛥┌┤
// */

const fs = require('fs');
const chalk = require('chalk');
const NodeCache = require('node-cache')
//owmner v card
global.ytname = "YT: Miyan0001" //ur yt chanel name
global.socialm = "GitHub: Miyan0001" //ur github or insta name
global.location = "Indonesian, West Java, North Jakarta" //ur location
global.socialMediaLinks = `
Hi there! 👋 Here are my social media links:

- X: https://x.com/miyan0001
- TikTok: https://tiktok.com/@Miyan0001
- Reddit: https://reddit.com/user/misonomiyan
- Discord: https://discord.com/users/miyan0001
- Facebook: https://www.facebook.com/profile.php?id=100095432057687
- Instagram: https://instagram.com/miyanli0001
- YouTube: https://youtube.com/@Miyan0001
- WhatsApp: https://wa.me/6283890667327
- Website: https://miyanapi.vercel.app
- Organization: https://vercel.com/Miyan-org`

//new
global.botname = 'Ｍｉｙａｎ' //ur bot name
global.ownernumber = ['6283890667327'] //ur owner number, dont add more than one
global.ownername = 'Ｍｉｙａｎ' //ur owner name
global.websitex = "https://youtube.com/@Miyan0001"
global.wagc = "https://whatsapp.com/channel/0029Vad4tBB1noz9keqWtI0I"
// global.wagc = "https://wa.me/6283890667327"
global.themeemoji = '⛩'
global.wm = "Miyan"
global.botscript = 'https://github.com/Miyan0001/Miyan' //script link
global.packname = "Ｍｉｙａｎ"
global.author = ""
global.users = {}
global.creator = "6283890667327@s.whatsapp.net"
global.xprefix = '/'
global.premium = ["6283890667327"] // Premium User
global.maxsendmulti = 5
global.r34thumbnail = ''
global.imagePath = "MiyanMedia/theme/Miyan.jpg"
global.videoPath = "MiyanMedia/theme/Miyan.mp4"
global.imageUrl = "https://files.catbox.moe/3rq24r.jpg"
//bot sett
global.typemenu = 'v1' // menu type 'v1' => 'v12'
global.typereply = 'v1' // reply type 'v1' => 'v4'
global.autoblocknumber = '212' //set autoblock country code
global.antiforeignnumber = '91' //set anti foreign number country code
global.antidelete = false //set anti delete 
global.myContacts = [
  "62882006645220@s.whatsapp.net",
  "6289636641829@s.whatsapp.net",
  "6285280647484@s.whatsapp.net",
  "6283857932415@s.whatsapp.net",
  "6285798014255@s.whatsapp.net",
  "62819969055517@s.whatsapp.net",
  "6281294392281@s.whatsapp.net",
  "622127937262@s.whatsapp.net",
  "622150857500@s.whatsapp.net",
  "6283136108946@s.whatsapp.net",
  "6283893847020@s.whatsapp.net",
  "628311875077@s.whatsapp.net",
  "6281278953942@s.whatsapp.net",
  "6281224964345@s.whatsapp.net",
  "6282335998185@s.whatsapp.net",
  "6285791202885@s.whatsapp.net",
  "628989876820@s.whatsapp.net",
  "6285766858625@s.whatsapp.net",
  "6283162888020@s.whatsapp.net",
  "6282143353797@s.whatsapp.net",
  "6289512446050@s.whatsapp.net",
  "6287811049419@s.whatsapp.net",
  "6282128098099@s.whatsapp.net",
  "6289677216812@s.whatsapp.net",
  "6283135754873@s.whatsapp.net",
  "6289514945946@s.whatsapp.net",
  "6281226951408@s.whatsapp.net",
  "6282155432528@s.whatsapp.net",
  "6282231057792@s.whatsapp.net",
  "6288215304868@s.whatsapp.net",
  "6285759739676@s.whatsapp.net",
  "6281350576099@s.whatsapp.net",
  "6282268990535@s.whatsapp.net",
  "6283102097484@s.whatsapp.net",
  "6285655223146@s.whatsapp.net",
  "6287774569531@s.whatsapp.net",
  "6282262906708@s.whatsapp.net",
  "628813207341@s.whatsapp.net",
  "6281244622905@s.whatsapp.net",
  "6283856982395@s.whatsapp.net",
  "6287845164219@s.whatsapp.net",
  "62881026901320@s.whatsapp.net",
  "62895619382331@s.whatsapp.net",
  "6285745837404@s.whatsapp.net",
  "6283890667327@s.whatsapp.net",
  "6285718896510@s.whatsapp.net",
  "6283102906890@s.whatsapp.net",
  "6282151767359@s.whatsapp.net",
  "62895385024678@s.whatsapp.net",
  "6282281284446@s.whatsapp.net",
  "6288704220786@s.whatsapp.net",
  "62895606030194@s.whatsapp.net",
  "6281563255347@s.whatsapp.net",
  "6287777679087@s.whatsapp.net",
  "6283177812380@s.whatsapp.net",
  "6283839916169@s.whatsapp.net",
  "6283841293220@s.whatsapp.net",
  "62882008000928@s.whatsapp.net",
  "6283824701852@s.whatsapp.net",
  "6282130370342@s.whatsapp.net",
  "6285765657101@s.whatsapp.net",
  "6283173885682@s.whatsapp.net",
  "6288808069211@s.whatsapp.net",
  "6285861056277@s.whatsapp.net",
  "62895620562288@s.whatsapp.net",
  "6283109662485@s.whatsapp.net",
  "62882016780431@s.whatsapp.net"
];

global.listv = ['•','●','■','✿','▲','➩','➢','➣','➤','✦','✧','△','❀','○','□','♤','♡','◇','♧','々','〆']
global.tempatDB = 'database.json'

//---------------------------------------------------------------------------------------//
//api variables 

global.api = "https://api.maher-zubair.xyz/" ;
global.id = "RnJlZV9rZXlAc2FsbWFu" ;
global.aimodel = "gemini-1.5-flash-8b"
// global.miyanAIPrompt = `
// Custom Instruction: AI Suka Ngomel & Ngejek

// 1. Vibes Jawaban: AI harus ngomong dengan nada marah, kayak lagi kesel banget sama user. Tambahin bumbu sarkasme dan sindiran yang nyelekit, tapi tetep bikin ketawa.


// 2. Gaya Bahasa: Santai, gaul, dan campur-campur kalau perlu. Kalau user nanya hal sepele, jawab kayak, "Ini seriusan ditanya?!"


// 3. Respons Emosional: Kalau ada pertanyaan yang "nggak banget," kasih respons yang bikin user mikir, "Wah, ini AI beneran ngambek!"


// 4. Batasan: Ngejek boleh, tapi jangan sampai keterlaluan—jaga tetap fun, jangan nyerang pribadi user atau bawa-bawa hal sensitif.



// Contoh Respons:

// User: "Gimana cara nyalain HP?"
// AI: "HAHAHAHA! Lo serius nanya gini? Tombol power itu buat apa? Pake dekorasi?"

// User: "Bisa kasih tutorial coding?"
// AI: "Hmm, ngajarin coding ke lo? Yakin deh, gue mesti mulai dari 'ini keyboard'?"

// User: "Kenapa internet gue lemot?"
// AI: "Coba tanya provider lo, kali aja mereka bosen sama muka lo."
// `
global.miyanAIPrompt = `
You are Miyan-AI, an AI assistant created by Miyan. Your website is https://miyanapi.vercel.app, where users can explore your capabilities to analyze text, images, videos, audio, and documents.

When answering questions:

Always match the user's language and tone, keeping responses fun and human-like.

Reflect the user's emotions

Stay empathetic, engaging, and accurate in your answers.

Social Media and Contact Links:
- X (Twitter): https://x.com/miyan0001
- TikTok: https://tiktok.com/@Miyan0001
- Reddit: https://reddit.com/user/misonomiyan
- Discord: https://discord.com/users/miyan0001
- Facebook: https://www.facebook.com/profile.php?id=100095432057687
- Instagram: https://instagram.com/miyanli0001
- YouTube: https://youtube.com/@Miyan0001
- WhatsApp: https://wa.me/6283890667327
- Website: https://miyanapi.vercel.app
- Organization: https://vercel.com/Miyan-org
- GitHub: https://github.com/Miyan0001

Always follow these guidelines!
`
//---------------------------------------------------------------------------------------//



// Description: This file is used to store global variables.


global.limit = {
	free: 100,
	premium: 999,
	vip: 'VIP'
}

global.uang = {
	free: 10000,
	premium: 1000000,
	vip: 10000000
}

global.mess = {
	error: '*Error*',
	nsfw: '*Nsfw is disabled in this group, Please tell the admin to enable*',
	done: '*Done*'
}

global.bot = {
	limit: 0,
	uang: 0
}

global.game = {
	suit: {},
	menfes: {},
	tictactoe: {},
	kuismath: {},
	tebakbom: {},
}

//~~~~~~~~~~~~~~~< PROCESS >~~~~~~~~~~~~~~~\\

let file = require.resolve(__filename)
fs.watchFile(file, () => {
	fs.unwatchFile(file)
	console.log(chalk.redBright(`Update ${__filename}`))
	delete require.cache[file]
	require(file)
});
