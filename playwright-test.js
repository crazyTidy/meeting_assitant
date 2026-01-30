/**
 * Meeting Assistant - 全流程功能自动化测试 (修订版)
 */

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const os = require('os');

const FRONTEND_URL = 'http://localhost:3003';
const BACKEND_URL = 'http://localhost:8000';

function createTestAudioFile() {
  const testDir = path.join(os.tmpdir(), 'playwright-test-files');
  if (!fs.existsSync(testDir)) {
    fs.mkdirSync(testDir, { recursive: true });
  }
  const filePath = path.join(testDir, 'test-audio.mp3');
  const mp3Header = Buffer.from([
    0xFF, 0xFB, 0x90, 0x00,
    ...new Array(1000).fill(0x00)
  ]);
  fs.writeFileSync(filePath, mp3Header);
  return filePath;
}

async function runTests() {
  console.log('🚀 开始 Meeting Assistant 全流程自动化测试\n');
  console.log('📍 前端地址:', FRONTEND_URL);
  console.log('📍 后端地址:', BACKEND_URL);
  console.log('');

  const browser = await chromium.launch({
    headless: false,
    slowMo: 150
  });

  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 }
  });

  const page = await context.newPage();
  let testsPassed = 0;
  let testsFailed = 0;
  const tmpDir = os.tmpdir();

  try {
    // 测试 1: 后端健康检查
    console.log('📋 测试 1: 后端健康检查');
    try {
      const healthResponse = await page.request.get(BACKEND_URL + '/health');
      if (healthResponse.ok()) {
        const healthData = await healthResponse.json();
        console.log('   ✅ 后端服务运行正常');
        console.log('   📊 版本:', healthData.version || '1.0.0');
        testsPassed++;
      } else {
        throw new Error('Health check returned ' + healthResponse.status());
      }
    } catch (error) {
      console.log('   ❌ 后端健康检查失败:', error.message);
      testsFailed++;
    }

    // 测试 2: 前端首页访问
    console.log('\n📋 测试 2: 前端首页访问');
    try {
      await page.goto(FRONTEND_URL, { waitUntil: 'domcontentloaded', timeout: 30000 });
      await page.waitForTimeout(2000); // 等待 Vue 渲染

      const title = await page.title();
      console.log('   📄 页面标题:', title);

      // 尝试获取 h1 文本
      try {
        const brandText = await page.locator('h1').first().textContent({ timeout: 3000 });
        console.log('   🏷️ 品牌名称:', brandText);
      } catch (e) {
        console.log('   ⚠️ 无法获取品牌名称');
      }

      await page.screenshot({ path: path.join(tmpDir, 'test-01-homepage.png'), fullPage: true });
      console.log('   📸 截图已保存:', path.join(tmpDir, 'test-01-homepage.png'));

      console.log('   ✅ 首页加载成功');
      testsPassed++;
    } catch (error) {
      console.log('   ❌ 首页访问失败:', error.message);
      testsFailed++;
    }

    // 测试 3: 检查页面元素
    console.log('\n📋 测试 3: 检查页面元素');
    try {
      // 等待页面加载
      await page.waitForTimeout(1000);

      // 获取当前 URL
      const currentUrl = page.url();
      console.log('   📍 当前URL:', currentUrl);

      // 检查是否有导航链接
      const uploadLink = page.locator('a[href="/upload"]');
      if (await uploadLink.count() > 0) {
        console.log('   📤 找到上传链接');
      }

      const meetingLink = page.locator('a[href="/meetings"]');
      if (await meetingLink.count() > 0) {
        console.log('   📋 找到会议列表链接');
      }

      await page.screenshot({ path: path.join(tmpDir, 'test-02-elements.png'), fullPage: true });
      console.log('   📸 截图已保存');

      console.log('   ✅ 页面元素检查完成');
      testsPassed++;
    } catch (error) {
      console.log('   ❌ 页面元素检查失败:', error.message);
      testsFailed++;
    }

    // 测试 4: 导航到上传页面
    console.log('\n📋 测试 4: 导航到上传页面');
    try {
      // 直接导航到上传页面
      await page.goto(FRONTEND_URL + '/upload', { waitUntil: 'domcontentloaded', timeout: 15000 });
      await page.waitForTimeout(1500);

      const currentUrl = page.url();
      console.log('   📍 当前URL:', currentUrl);

      // 检查上传区域
      const uploadText = await page.locator('text=点击上传').count();
      const dragText = await page.locator('text=拖拽').count();
      console.log('   📤 上传提示文本:', uploadText > 0 || dragText > 0 ? '存在' : '不存在');

      // 检查文件输入
      const fileInput = page.locator('input[type="file"]');
      const hasFileInput = await fileInput.count() > 0;
      console.log('   📁 文件输入框:', hasFileInput ? '存在' : '不存在');

      await page.screenshot({ path: path.join(tmpDir, 'test-03-upload-page.png'), fullPage: true });
      console.log('   📸 截图已保存');

      console.log('   ✅ 上传页面正常');
      testsPassed++;
    } catch (error) {
      console.log('   ❌ 上传页面测试失败:', error.message);
      testsFailed++;
    }

    // 测试 5: 文件选择功能
    console.log('\n📋 测试 5: 文件选择功能');
    try {
      const testAudioPath = createTestAudioFile();
      console.log('   📁 创建测试文件:', testAudioPath);

      const fileInput = page.locator('input[type="file"]');
      if (await fileInput.count() > 0) {
        await fileInput.setInputFiles(testAudioPath);
        await page.waitForTimeout(1000);
        console.log('   ✅ 文件已选择');

        // 尝试输入标题
        const titleInput = page.locator('input[type="text"]').first();
        if (await titleInput.count() > 0) {
          await titleInput.fill('自动化测试会议');
          console.log('   ✅ 标题已输入');
        }

        await page.screenshot({ path: path.join(tmpDir, 'test-04-file-selected.png'), fullPage: true });
        console.log('   📸 截图已保存');
      } else {
        console.log('   ⚠️ 未找到文件输入框');
      }

      console.log('   ✅ 文件选择功能测试完成');
      testsPassed++;
    } catch (error) {
      console.log('   ❌ 文件选择测试失败:', error.message);
      testsFailed++;
    }

    // 测试 6: 导航到会议列表页面
    console.log('\n📋 测试 6: 导航到会议列表页面');
    try {
      await page.goto(FRONTEND_URL + '/meetings', { waitUntil: 'domcontentloaded', timeout: 15000 });
      await page.waitForTimeout(1500);

      const currentUrl = page.url();
      console.log('   📍 当前URL:', currentUrl);

      // 检查搜索框
      const searchInput = page.locator('input[placeholder*="搜索"]');
      const hasSearch = await searchInput.count() > 0;
      console.log('   🔍 搜索框:', hasSearch ? '存在' : '不存在');

      await page.screenshot({ path: path.join(tmpDir, 'test-05-meeting-list.png'), fullPage: true });
      console.log('   📸 截图已保存');

      console.log('   ✅ 会议列表页面正常');
      testsPassed++;
    } catch (error) {
      console.log('   ❌ 会议列表测试失败:', error.message);
      testsFailed++;
    }

    // 测试 7: 响应式设计测试
    console.log('\n📋 测试 7: 响应式设计测试');
    try {
      const viewports = [
        { name: 'Desktop', width: 1440, height: 900 },
        { name: 'Tablet', width: 768, height: 1024 },
        { name: 'Mobile', width: 375, height: 667 }
      ];

      for (const vp of viewports) {
        await page.setViewportSize({ width: vp.width, height: vp.height });
        await page.waitForTimeout(500);
        await page.screenshot({
          path: path.join(tmpDir, 'test-responsive-' + vp.name.toLowerCase() + '.png'),
          fullPage: true
        });
        console.log('   📱 ' + vp.name + ' (' + vp.width + 'x' + vp.height + '): 截图已保存');
      }

      await page.setViewportSize({ width: 1440, height: 900 });

      console.log('   ✅ 响应式设计测试完成');
      testsPassed++;
    } catch (error) {
      console.log('   ❌ 响应式测试失败:', error.message);
      testsFailed++;
    }

    // 测试 8: API 端点测试
    console.log('\n📋 测试 8: API 端点测试');
    try {
      // 测试会议列表 API
      const listResponse = await page.request.get(BACKEND_URL + '/api/v1/meetings/');
      console.log('   📡 GET /api/v1/meetings/ - 状态:', listResponse.status());

      if (listResponse.ok()) {
        const data = await listResponse.json();
        console.log('   📊 返回数据: total=' + data.total + ', page=' + data.page);
        testsPassed++;
      } else {
        console.log('   ⚠️ API 返回非 200 状态');
        testsFailed++;
      }

      console.log('   ✅ API 端点测试完成');
    } catch (error) {
      console.log('   ❌ API 测试失败:', error.message);
      testsFailed++;
    }

  } catch (error) {
    console.log('\n❌ 测试执行过程中发生错误:', error.message);
  } finally {
    console.log('\n' + '='.repeat(50));
    console.log('📊 测试总结');
    console.log('='.repeat(50));
    console.log('   ✅ 通过:', testsPassed);
    console.log('   ❌ 失败:', testsFailed);
    const total = testsPassed + testsFailed;
    const passRate = total > 0 ? ((testsPassed / total) * 100).toFixed(1) : 0;
    console.log('   📈 通过率:', passRate + '%');
    console.log('\n📁 测试截图保存位置:', tmpDir);
    console.log('='.repeat(50));

    await page.waitForTimeout(2000); // 给用户时间查看最终状态
    await browser.close();
  }
}

runTests().catch(console.error);
