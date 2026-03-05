# Token 演示功能说明

## 快速开始

### 1. 生成测试 Token

运行以下命令生成两个测试用户的 Token：

```bash
cd meeting-assistant-backend
python generate_tokens.py
```

输出示例：
```
【用户 1】研发部 - 张三
Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

【用户 2】市场部 - 李四
Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 2. 通过 API 获取 Token

```bash
curl http://localhost:8000/api/v1/demo/tokens
```

返回两个用户的 Token 信息。

## API 接口

### 1. 获取测试 Token
```
GET /api/v1/demo/tokens
```

返回两个测试用户的 Token，可直接复制使用。

### 2. 解析当前 Token
```
GET /api/v1/demo/parse-token
Header: Authorization: Bearer <token>
```

解析并显示当前 Token 中的用户信息。

### 3. 切换用户（演示）
```
POST /api/v1/demo/switch-user
Body: { "token": "<token>" }
```

切换到指定用户。

## 前端使用示例

### JavaScript/Fetch

```javascript
// 用户1: 张三的 Token
const token1 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...";

// 获取当前用户信息
fetch('http://localhost:8000/api/v1/users/me', {
  headers: {
    'Authorization': `Bearer ${token1}`
  }
})
.then(res => res.json())
.then(data => console.log(data));

// 创建会议（会关联到张三）
const formData = new FormData();
formData.append('title', '张三的会议');
formData.append('audio', audioFile);

fetch('http://localhost:8000/api/v1/meetings/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token1}`
  },
  body: formData
});

// 查看张三的会议列表
fetch('http://localhost:8000/api/v1/meetings/', {
  headers: {
    'Authorization': `Bearer ${token1}`
  }
});
```

### Axios

```javascript
import axios from 'axios';

// 设置默认 Token
axios.defaults.headers.common['Authorization'] = `Bearer ${token1}`;

// 获取当前用户
axios.get('/api/v1/users/me');

// 创建会议
axios.post('/api/v1/meetings/', formData);

// 会议列表（自动使用当前用户）
axios.get('/api/v1/meetings/');
```

### Vue 3

```vue
<script setup>
import { ref } from 'vue';
import axios from 'axios';

const currentUser = ref(null);
const meetings = ref([]);

// 用户1 Token
const token1 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...";

// 获取当前用户
const getCurrentUser = async () => {
  const res = await axios.get('/api/v1/users/me', {
    headers: { Authorization: `Bearer ${token1}` }
  });
  currentUser.value = res.data;
};

// 获取会议列表
const getMeetings = async () => {
  const res = await axios.get('/api/v1/meetings/', {
    headers: { Authorization: `Bearer ${token1}` }
  });
  meetings.value = res.data.items;
};

getCurrentUser();
getMeetings();
</script>
```

## 测试流程

### 1. 用户隔离测试

```bash
# 使用张三的 Token 创建会议
export TOKEN="eyJhbG...张三的token"
curl -H "Authorization: Bearer $TOKEN" \
     -F "title=张三的会议" \
     -F "audio=@test.mp3" \
     http://localhost:8000/api/v1/meetings/

# 查看张三的会议（能看到刚创建的）
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/v1/meetings/

# 切换到李四的 Token
export TOKEN="eyJhbG...李四的token"
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/v1/meetings/

# 李四看不到张三的会议（用户隔离）
```

### 2. cURL 快速测试

```bash
# 1. 获取测试 Token
curl http://localhost:8000/api/v1/demo/tokens

# 2. 使用 Token1（张三）
TOKEN="粘贴张三的token"

# 3. 获取当前用户信息
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/v1/users/me

# 4. 解析 Token
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/v1/demo/parse-token

# 5. 查看会议列表
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/v1/meetings/
```

## 浏览器开发者工具测试

1. 打开浏览器开发者工具（F12）

2. 在 Console 中运行：
```javascript
// 保存 Token
localStorage.setItem('token', '粘贴张三的token');

// 读取 Token
const token = localStorage.getItem('token');

// 测试请求
fetch('/api/v1/users/me', {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json()).then(console.log);
```

## Token 说明

### Token 结构

```
Header: {"alg": "HS256", "typ": "JWT"}
Payload:
{
  "sub": "user-001",           # 用户ID（必需）
  "username": "zhangsan",      # 用户名
  "real_name": "张三",         # 真实姓名
  "department_id": "dept-001", # 部门ID
  "department_name": "研发部",  # 部门名称
  "position": "高级工程师",     # 职位
  "iat": 1234567890,          # 签发时间
  "exp": 1234567890           # 过期时间
}
```

### 生产环境配置

在 `.env` 文件中配置：

```bash
# JWT 密钥（生产环境必须修改）
JWT_SECRET_KEY=your-production-secret-key-here

# Token 过期时间（天）
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=10080

# 关闭开发模式（启用 JWT 认证）
DEV_MODE=false
```

## 注意事项

1. **开发模式**：`DEV_MODE=true` 时不需要 Token，使用测试用户
2. **生产模式**：`DEV_MODE=false` 时必须提供有效 Token
3. **Token 过期**：默认 365 天，可通过配置修改
4. **安全**：生产环境务必修改 `JWT_SECRET_KEY`
