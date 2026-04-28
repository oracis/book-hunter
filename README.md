# 📚 书海猎手 - Cloudflare Workers 部署指南

> v1.0.0 | 一个基于 Cloudflare Workers 的国内热门书籍实时搜索应用。

## 功能特性

- 🔍 **实时搜索** - 支持书名、作者多关键词搜索
- 📖 **多源聚合** - 当当网、豆瓣、京东
- 📥 **一键下载** - 每本书直链 Z-Library 搜索
- 🚀 **全球加速** - Cloudflare Workers 边缘部署
- 📱 **响应式设计** - 适配桌面和移动端

## 部署步骤

### 1. 安装 Wrangler CLI

```bash
npm install -g wrangler
```

### 2. 登录 Cloudflare

```bash
wrangler login
```

### 3. 部署到 Cloudflare

```bash
cd cloudflare-app
wrangler deploy
```

部署成功后，Cloudflare 会分配一个免费的子域名，格式类似：
`https://book-hunter.<your-subdomain>.workers.dev`

### 4. 访问应用

在浏览器打开分配给你的 Workers URL 即可使用！

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 前端页面 |
| `/api/books` | GET | 获取全部书籍 |
| `/api/search?q=关键词` | GET | 搜索书籍 |
| `/api/refresh` | GET | 刷新数据缓存 |
| `/api/health` | GET | 健康检查 |

## 数据来源

当前支持以下数据源：

1. **当当网** - 当当网图书畅销榜
2. **豆瓣** - 豆瓣图书热门榜单
3. **京东** - 京东图书畅销榜

> 注意：免费版 Workers 无法直接抓取部分网站，需要配置 Cloudflare Data Scraping Allowance 或使用代理。

## 技术架构

- **后端**: Cloudflare Workers (JavaScript)
- **前端**: 原生 HTML/CSS/JavaScript
- **缓存**: Cloudflare KV (可选)
- **部署**: Wrangler CLI

## 本地开发

```bash
cd cloudflare-app
wrangler dev
```

## 文件结构

```
cloudflare-app/
├── wrangler.toml      # Cloudflare 配置
├── src/
│   └── index.js       # Workers 后端代码
└── public/
    └── index.html     # 前端页面
```

## 扩展建议

1. **添加更多数据源** - 微信读书、知乎图书等
2. **启用 KV 缓存** - 减少重复抓取，提升响应速度
3. **添加评分系统** - 用户可以对书籍进行评分
4. **收藏功能** - 使用 Cloudflare D1 数据库

## License

MIT
