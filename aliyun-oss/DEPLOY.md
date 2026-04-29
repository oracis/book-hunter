# 部署到阿里云 OSS（国内可访问）

## 前提条件

- 阿里云账号 + 备案过的域名 `ydtgo.top`
- 域名已备案（国内 OSS 必须域名备案）

---

## 第一步：阿里云控制台配置

### 1.1 创建 OSS Bucket

1. 进入 [阿里云 OSS 控制台](https://oss.console.aliyun.com)
2. 点击「创建 Bucket」
3. 填写信息：
   - **Bucket 名称**：`book-hunter`（或你喜欢的名字）
   - **地域**：选择离你最近的，比如 `华东 1（杭州）`
   - **存储类型**：标准存储
   - **读写权限**：**公共读**（否则网站无法访问）
4. 点击「确定」

### 1.2 开启静态网站托管

1. 进入刚创建的 Bucket
2. 左侧菜单 → 「数据管理」→「静态网站托管」
3. 点击「设置」
4. 填写：
   - **默认首页**：`index.html`
   - **默认 404 页**：`index.html`（SPA 模式，全部重定向到首页）
5. 点击「保存」

### 1.3 获取 OSS 外网 Endpoint

1. Bucket 左侧菜单 → 「概览」
2. 找到「Endpoint（外网）」，格式类似：
   ```
   book-hunter.oss-cn-hangzhou.aliyuncs.com
   ```
3. 复制备用

### 1.4 绑定自定义域名

1. Bucket 左侧菜单 → 「域名管理」
2. 点击「绑定域名」
3. 输入：`ydtgo.top`
4. 勾选「自动添加 CNAME 记录」（如果你的域名在阿里云解析）
5. 点击「确认」

> 如果域名在其他注册商，需要手动添加 CNAME 记录：
> - **记录类型**：CNAME
> - **主机记录**：@
> - **记录值**：填入上面 1.3 的 Endpoint，如 `book-hunter.oss-cn-hangzhou.aliyuncs.com`

---

## 第二步：创建 AccessKey（建议使用 RAM 用户）

1. 进入 [RAM 控制台](https://ram.console.aliyun.com)
2. 左侧「人员管理」→「用户」→「创建用户」
3. 填写用户名：`book-hunter-deploy`
4. 勾选「Open API 调用访问」
5. 保存 **AccessKey ID** 和 **AccessKey Secret**

### 给 RAM 用户授权

1. 用户列表 → 找到 `book-hunter-deploy` → 点击「添加权限」
2. 搜索并添加以下权限：
   - `AliyunOSSFullAccess`（OSS 完全访问权限）
   - 或者更精确地，只给这个 Bucket 的写权限

---

## 第三步：配置 GitHub Secrets

1. 打开 GitHub 仓库：`https://github.com/oracis/book-hunter`
2. 进入 **Settings** → **Secrets and variables** → **Actions**
3. 点击「New repository secret」，添加以下 4 个 secrets：

| Secret 名称 | 值来源 |
|------------|--------|
| `OSS_ENDPOINT` | 1.3 中的 Endpoint，如 `oss-cn-hangzhou.aliyuncs.com` |
| `OSS_ACCESS_KEY_ID` | RAM 用户的 AccessKey ID |
| `OSS_ACCESS_KEY_SECRET` | RAM 用户的 AccessKey Secret |
| `OSS_BUCKET` | 你的 Bucket 名称，如 `book-hunter` |

---

## 第四步：触发部署

1. 进入仓库 **Actions** 标签页
2. 选择「Deploy to Aliyun OSS」workflow
3. 点击「Run workflow」
4. 等待约 1 分钟，检查是否成功

---

## 本地测试（可选）

如果想本地先测试，不用 GitHub Actions：

```bash
# 安装 ossutil
go install github.com/aliyun/ossutil/cmd/ossutil@latest

# 配置（交互式）
ossutil config

# 上传文件
ossutil cp -r ./aliyun-oss/ oss://你的bucket名称/ --force
```

---

## 部署完成后

访问 `https://ydtgo.top`（国内可直接打开）

---

## 如果不想用 GitHub Actions

也可以直接在阿里云控制台手动上传文件：
1. OSS 控制台 → Bucket → 「文件管理」
2. 点击「上传文件」，把 `aliyun-oss/index.html` 拖进去
3. 设置 HTTP 头：`Content-Type: text/html`
