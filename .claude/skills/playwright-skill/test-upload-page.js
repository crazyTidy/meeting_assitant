const { chromium } = require('playwright');
const path = require('path');

const TARGET_URL = 'http://localhost';

(async () => {
  const browser = await chromium.launch({ headless: false, slowMo: 100 });
  const page = await browser.newPage();

  try {
    console.log('🔍 访问上传页面...');
    await page.goto(`${TARGET_URL}/upload`, { waitUntil: 'networkidle', timeout: 15000 });

    console.log('✅ 页面加载成功');

    // 监听网络请求
    page.on('request', (request) => {
      if (request.url().includes('/api/')) {
        const headers = request.headers();
        console.log(`📤 API 请求: ${request.method()} ${request.url()}`);
        console.log(`   Content-Length: ${headers['content-length'] || 'N/A'}`);
      }
    });

    page.on('response', async (response) => {
      if (response.url().includes('/api/')) {
        const status = response.status();
        console.log(`📥 API 响应: ${response.url()} - 状态码: ${status}`);

        if (status === 413) {
          console.error('❌ 仍然存在 413 错误！Nginx 配置可能未生效。');
        } else if (status >= 400) {
          const body = await response.text().catch(() => '无法读取响应体');
          console.error(`❌ API 错误: ${body}`);
        } else {
          console.log('✅ 请求成功');
        }
      }
    });

    // 查找文件输入元素
    console.log('🔍 查找文件上传元素...');
    const fileInput = await page.locator('input[type="file"]').first();

    if (await fileInput.isVisible()) {
      console.log('✅ 找到文件输入元素');

      // 创建一个测试文件
      const testFilePath = path.join(__dirname, 'test-audio.txt');
      const fs = require('fs');
      fs.writeFileSync(testFilePath, 'This is a test audio file for upload testing');

      console.log('🔍 尝试上传测试文件...');
      await fileInput.setInputFiles(testFilePath);

      // 查找上传按钮
      const uploadButton = await page.locator('button').filter({ hasText: /上传|开始处理|提交/i }).first();

      if (await uploadButton.isVisible({ timeout: 5000 })) {
        console.log('✅ 找到上传按钮，点击上传...');
        await uploadButton.click();

        // 等待响应
        await page.waitForTimeout(5000);
      } else {
        console.log('⚠️ 未找到上传按钮，可能文件选择后自动上传');
        await page.waitForTimeout(5000);
      }

      // 清理测试文件
      fs.unlinkSync(testFilePath);

    } else {
      console.log('⚠️ 未找到文件输入元素');
    }

    // 截图
    await page.screenshot({ path: 'C:/tmp/upload-page-test.png', fullPage: true });
    console.log('📸 截图已保存到 C:/tmp/upload-page-test.png');

  } catch (error) {
    console.error('❌ 验证失败:', error.message);
  } finally {
    await browser.close();
  }

  console.log('\n✅ 验证完成');
  console.log('\n📝 修改总结:');
  console.log('- Nginx client_max_body_size: 1MB → 100M');
  console.log('- Nginx proxy_*_timeout: 60s → 300s');
  console.log('\n如果仍然出现 413 错误，请:');
  console.log('1. 在浏览器中按 Ctrl+F5 强制刷新');
  console.log('2. 检查容器配置: docker exec meeting-frontend cat /etc/nginx/conf.d/default.conf');
  console.log('3. 重启容器: docker-compose restart frontend');
})();
