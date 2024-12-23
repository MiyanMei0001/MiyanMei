const { chromium } = require('playwright');

async function generateImage(text) {
    const browser = await chromium.launch();
    try {
        const page = await browser.newPage();
        await page.goto('https://www.bratgenerator.com/');
        await page.click('#toggleButtonWhite');
        await page.locator('#textInput').fill(text);
        const output = `${text}.jpg`;
        await page.locator('#textOverlay').screenshot({ path: output });
        return output;
    } catch (e) {
        throw e;
    } finally {
        await browser.close();
    }
}

module.exports = generateImage;