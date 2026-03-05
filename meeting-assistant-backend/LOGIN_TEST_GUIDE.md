# 登录功能完整测试方案

## 一、环境准备

### 1.1 启动后端服务
```bash
cd meeting-assistant-backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 1.2 启动前端服务（新终端）
```bash
cd meeting-assistant-frontend
npm run dev
```

### 1.3 访问地址
- 前端：http://localhost:5173
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

---

## 二、后端API测试

### 2.1 自动化测试
```bash
cd meeting-assistant-backend
python test_token_login.py
```

**测试内容：**
- ✅ 生成两个测试用户的JWT Token
- ✅ 使用Token登录
- ✅ 获取当前用户信息
- ✅ 访问会议列表（验证用户隔离）
- ✅ 测试无效Token（应返回401）

### 2.2 手动API测试

#### 测试1: 获取应用配置
```bash
curl http://localhost:8000/api/v1/users/config
```

**预期响应：**
```json
{
  "dev_mode": true,
  "dev_user_info": {
    "user_id": "dev-user-001",
    "username": "dev_user",
    "real_name": "开发测试用户"
  },
  "version": "1.0.0",
  "app_name": "Meeting Assistant"
}
```

#### 测试2: 生成测试Token
```bash
cd meeting-assistant-backend
python -c "
from app.utils.jwt_generator import generate_test_token
token = generate_test_token(
    user_id='user-test',
    username='testuser',
    real_name='测试用户',
    department_id='dept-test',
    department_name='测试部门',
    position='测试职位'
)
print(token)
"
```

#### 测试3: Token登录
```bash
# 替换YOUR_TOKEN为上面生成的Token
curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{"token": "YOUR_TOKEN"}'
```

**预期响应：**
```json
{
  "access_token": "YOUR_TOKEN",
  "token_type": "bearer",
  "user": {
    "user_id": "user-test",
    "username": "testuser",
    "real_name": "测试用户",
    "department_name": "测试部门"
  }
}
```

#### 测试4: 开发模式登录
```bash
curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{"dev_mode": true}'
```

#### 测试5: 使用Token访问API
```bash
# 获取当前用户
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取会议列表
curl http://localhost:8000/api/v1/meetings/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 三、前端功能测试

### 3.1 开发模式登录测试
1. 访问 http://localhost:5173
2. 应自动跳转到登录页
3. 默认选中"开发模式"
4. 点击"进入系统"按钮
5. ✅ 应成功跳转到会议列表页
6. ✅ 顶部导航栏显示"开发测试用户"

### 3.2 Token模式登录测试
1. 在登录页点击"切换到Token登录"
2. 粘贴测试Token（从步骤2.2获取）
3. 点击"进入系统"按钮
4. ✅ 应成功跳转到会议列表页
5. ✅ 顶部导航栏显示Token对应的用户信息

### 3.3 路由守卫测试
1. 清除浏览器localStorage
   ```javascript
   localStorage.clear()
   ```
2. 直接访问 http://localhost:5173/meetings
3. ✅ 应自动跳转到登录页

### 3.4 登出功能测试
1. 登录后点击右上角的退出按钮
2. ✅ 应跳转到登录页
3. ✅ localStorage中的access_token被清除

---

## 四、用户隔离验证

### 4.1 准备两个不同的Token

**Token 1 - 张三（研发部）：**
```python
from app.utils.jwt_generator import generate_test_token
token1 = generate_test_token(
    user_id='user-zhangsan',
    username='zhangsan',
    real_name='张三',
    department_id='dept-rd',
    department_name='研发部',
    position='高级工程师'
)
print(token1)
```

**Token 2 - 李四（市场部）：**
```python
token2 = generate_test_token(
    user_id='user-lisi',
    username='lisi',
    real_name='李四',
    department_id='dept-market',
    department_name='市场部',
    position='市场经理'
)
print(token2)
```

### 4.2 验证步骤

#### 步骤1: 使用Token1登录并创建会议
```bash
# 登录
curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{"token": "TOKEN1"}'

# 创建会议（需要音频文件）
curl -X POST http://localhost:8000/api/v1/meetings/ \
  -F "title=张三的会议" \
  -F "audio=@test.mp3" \
  -H "Authorization: Bearer TOKEN1"
```

#### 步骤2: 使用Token2查看会议列表
```bash
curl http://localhost:8000/api/v1/meetings/ \
  -H "Authorization: Bearer TOKEN2"
```

**预期结果：**
- ✅ 看不到张三创建的会议（用户隔离生效）

#### 步骤3: 使用Token1查看会议列表
```bash
curl http://localhost:8000/api/v1/meetings/ \
  -H "Authorization: Bearer TOKEN1"
```

**预期结果：**
- ✅ 能看到自己创建的会议
- ✅ 所有会议的creator_id都是user-zhangsan

---

## 五、前端浏览器控制台测试

### 5.1 测试用户Store
```javascript
// 在浏览器控制台执行
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

// 测试开发模式登录
await userStore.devLogin()
console.log('User:', userStore.user)
console.log('Is Logged In:', userStore.isLoggedIn)

// 测试Token登录
await userStore.login({ token: 'YOUR_TOKEN' })
console.log('User:', userStore.user)

// 测试登出
await userStore.logout()
console.log('Is Logged In:', userStore.isLoggedIn)
```

### 5.2 测试用户API
```javascript
// 测试登录接口
const response = await fetch('/api/v1/users/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ dev_mode: true })
})
console.log('Login response:', await response.json())

// 测试获取用户信息
const me = await fetch('/api/v1/users/me')
console.log('Current user:', await me.json())
```

---

## 六、常见问题排查

### 问题1: Token登录返回401
**原因：** Token无效或过期
**解决：** 重新生成Token

### 问题2: 无法访问会议列表
**原因：** 中间件拦截了请求
**解决：** 确保Authorization header正确设置

### 问题3: 开发模式下所有请求返回开发用户
**原因：** dev_auth_middleware总是注入开发用户
**说明：** 这是正常行为，开发模式用于快速测试

### 问题4: 前端无法连接后端
**原因：** 后端未启动或端口错误
**解决：** 检查后端是否在8000端口运行

---

## 七、测试检查清单

### 后端测试
- [ ] 配置接口返回正确的开发模式状态
- [ ] Token登录成功并返回用户信息
- [ ] 开发模式登录成功
- [ ] 无效Token返回401
- [ ] 空Token返回400
- [ ] /users/me接口返回当前用户
- [ ] 会议列表自动筛选当前用户的会议

### 前端测试
- [ ] 访问系统自动跳转到登录页
- [ ] 开发模式登录成功
- [ ] Token模式登录成功
- [ ] 登录后跳转到会议列表
- [ ] 顶部显示正确的用户信息
- [ ] 登出功能正常
- [ ] 未登录访问受保护页面跳转到登录页

### 用户隔离测试
- [ ] 不同Token只能看到自己的会议
- [ ] 创建会议自动关联当前用户
- [ ] 切换Token后看到不同的会议列表

---

## 八、快速验证命令

```bash
# 一键测试所有功能
cd meeting-assistant-backend
python test_token_login.py && python test_user_isolation.py

# 预期输出：所有测试步骤显示Success!
```

---

## 九、生产环境配置

切换到生产模式，编辑 `meeting-assistant-backend/.env`：
```env
DEV_MODE=False
JWT_SECRET_KEY=your-production-secret-key
```

重启后端服务，此时：
- 开发模式登录不可用
- 必须使用有效的JWT Token
- 中间件会严格验证Token

---

## 十、联系支持

如有问题，请检查：
1. 后端日志：`/tmp/backend.log`
2. 浏览器控制台：F12 -> Console
3. 网络请求：F12 -> Network
