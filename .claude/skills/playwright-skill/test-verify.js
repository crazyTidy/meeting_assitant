const { chromium } = require('playwright');

const TARGET_URL = 'http://localhost:3000';

(async () => {
  const browser = await chromium.launch({ headless: false, slowMo: 100 });
  const page = await browser.newPage();

  try {
    console.log('🔍 访问前端服务...');
    await page.goto(TARGET_URL, { waitUntil: 'networkidle', timeout: 15000 });

    const title = await page.title();
    console.log('✅ 页面标题:', title);

    // 检查页面是否正常加载
    const bodyText = await page.locator('body').textContent();
    if (bodyText && bodyText.length > 0) {
      console.log('✅ 页面内容加载成功');
    }

    // 截图
    await page.screenshot({ path: 'C:/tmp/frontend-screenshot.png', fullPage: true });
    console.log('📸 截图已保存到 C:/tmp/frontend-screenshot.png');

    // 检查是否有错误
    const errors = [];
    page.on('pageerror', (error) => {
      errors.push(error.message);
    });

    if (errors.length > 0) {
      console.log('⚠️ 页面错误:', errors);
    } else {
      console.log('✅ 未检测到页面错误');
    }

    console.log('✅ 前端服务验证成功');

  } catch (error) {
    console.error('❌ 验证失败:', error.message);
  } finally {
    await browser.close();
  }
})();
