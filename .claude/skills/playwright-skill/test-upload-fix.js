const { chromium } = require('playwright');

const TARGET_URL = 'http://localhost';

(async () => {
  const browser = await chromium.launch({ headless: false, slowMo: 100 });
  const page = await browser.newPage();

  try {
    console.log('🔍 访问应用...');
    await page.goto(TARGET_URL, { waitUntil: 'networkidle', timeout: 15000 });

    console.log('✅ 页面加载成功');

    // 点击上传按钮
    console.log('🔍 查找上传按钮...');
    const uploadButton = await page.locator('button').filter({ hasText: /上传|upload/i }).first();

    if (await uploadButton.isVisible()) {
      console.log('✅ 找到上传按钮');

      // 监听网络请求以查看上传请求的详情
      page.on('request', (request) => {
        if (request.url().includes('/api/')) {
          console.log(`📤 API 请求: ${request.method()} ${request.url()}`);
        }
      });

      page.on('response', async (response) => {
        if (response.url().includes('/api/')) {
          const status = response.status();
          console.log(`📥 API 响应: ${response.url()} - 状态码: ${status}`);

          if (status === 413) {
            console.error('❌ 仍然存在 413 错误！');
          } else if (status >= 400) {
            const body = await response.text().catch(() => '无法读取响应体');
            console.error(`❌ API 错误: ${body}`);
          } else {
            console.log('✅ 请求成功');
          }
        }
      });

      // 点击上传按钮
      await uploadButton.click();

      // 等待一下看看是否有对话框或错误
      await page.waitForTimeout(3000);

      console.log('\n📝 检查 Nginx 配置是否生效...');
      console.log('已设置 client_max_body_size 为 100M');

    } else {
      console.log('⚠️ 未找到上传按钮');
    }

    // 截图
    await page.screenshot({ path: 'C:/tmp/upload-test-screenshot.png', fullPage: true });
    console.log('📸 截图已保存');

  } catch (error) {
    console.error('❌ 验证失败:', error.message);
  } finally {
    await browser.close();
  }

  console.log('\n✅ 验证完成');
  console.log('如果仍然出现 413 错误，请：');
  console.log('1. 刷新浏览器页面（Ctrl+F5）');
  console.log('2. 清除浏览器缓存');
  console.log('3. 检查 Docker 日志: docker-compose logs frontend');
})();
