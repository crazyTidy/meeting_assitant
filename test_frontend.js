const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  // Go to meeting detail page
  await page.goto('http://localhost:3002/meetings/d1e36e1c-13e0-4b76-9b00-b6c174c857c3');

  // Wait for page to load
  await page.waitForTimeout(5000);

  // Take screenshot
  await page.screenshot({ path: 'screenshot.png' });
  console.log('Screenshot saved to screenshot.png');

  // Check if timeline data is displayed
  const timelineItems = await page.locator('v-for').count();
  console.log('Timeline items found:', timelineItems);

  // Get page content
  const content = await page.content();
  console.log('Page contains "逐字稿":', content.includes('逐字稿'));
  console.log('Page contains "说话人1":', content.includes('说话人1'));

  await browser.close();
})();
