/**
 * Book Hunter - 国内热门书籍实时搜索
 * Cloudflare Workers 后端
 */

// 书籍来源列表
const BOOK_SOURCES = {
  dangdang: {
    name: '当当网',
    url: 'https://category.dangdang.com/cp01.54.00.00.00.00.html',
    listSelector: '..list_ul .line1',
    parser: parseDangdang
  },
  douban: {
    name: '豆瓣',
    url: 'https://book.douban.com/chart',
    parser: parseDouban
  },
  jd: {
    name: '京东',
    url: 'https://book.jd.com/booksort.html',
    parser: parseJD
  }
};

// 模拟书籍数据（用于开发和免费层测试）
const MOCK_BOOKS = [
  { title: '活着', author: '余华', source: '当当网', rating: '9.4', year: '2012' },
  { title: '平凡的世界', author: '路遥', source: '当当网', rating: '9.0', year: '2017' },
  { title: '三体', author: '刘慈欣', source: '豆瓣', rating: '9.5', year: '2021' },
  { title: '人类简史', author: '尤瓦尔·赫拉利', source: '京东', rating: '9.1', year: '2022' },
  { title: '被讨厌的勇气', author: '岸见一郎', source: '当当网', rating: '8.8', year: '2023' },
  { title: '认知觉醒', author: '周岭', source: '豆瓣', rating: '8.6', year: '2024' },
  { title: '百年孤独', author: '加西亚·马尔克斯', source: '当当网', rating: '9.3', year: '2011' },
  { title: '明朝那些事儿', author: '当年明月', source: '京东', rating: '9.2', year: '2023' },
  { title: '小王子', author: '圣埃克苏佩里', source: '当当网', rating: '9.7', year: '2018' },
  { title: '解忧杂货店', author: '东野圭吾', source: '豆瓣', rating: '8.5', year: '2024' },
  { title: 'python编程 从入门到实践', author: '埃里克·马瑟斯', source: '京东', rating: '9.0', year: '2023' },
  { title: '设计模式下', author: '程杰', source: '当当网', rating: '9.4', year: '2020' },
  { title: 'javascript高级程序设计', author: '马特·弗劳恩', source: '京东', rating: '9.2', year: '2023' },
  { title: '蛤蟆先生去看心理医生', author: '罗伯特·戴博德', source: '豆瓣', rating: '8.7', year: '2024' },
  { title: '追风筝的人', author: '卡勒德·胡赛尼', source: '当当网', rating: '9.1', year: '2019' },
  { title: '遥远的救世主', author: '豆豆', source: '当当网', rating: '8.8', year: '2023' },
  { title: '置身事内', author: '兰小欢', source: '豆瓣', rating: '9.1', year: '2024' },
  { title: '原则', author: '瑞·达利欧', source: '京东', rating: '8.9', year: '2022' },
  { title: '穷爸爸富爸爸', author: '罗伯特·清崎', source: '当当网', rating: '8.5', year: '2023' },
  { title: '高效能人士的七个习惯', author: '史蒂芬·柯维', source: '京东', rating: '9.0', year: '2021' },
  { title: '中国哲学简史', author: '冯友兰', source: '豆瓣', rating: '9.3', year: '2024' },
  { title: '万历十五年', author: '黄仁宇', source: '当当网', rating: '9.2', year: '2022' },
  { title: '乌合之众', author: '古斯塔夫·勒庞', source: '京东', rating: '8.6', year: '2023' },
  { title: '自卑与超越', author: '阿德勒', source: '豆瓣', rating: '8.7', year: '2024' },
  { title: '思考快与慢', author: '丹尼尔·卡尼曼', source: '当当网', rating: '9.1', year: '2022' },
  { title: '刻意练习', author: '安德斯·艾利克森', source: '京东', rating: '8.8', year: '2023' },
  { title: '非暴力沟通', author: '马歇尔·卢森堡', source: '豆瓣', rating: '8.9', year: '2024' },
  { title: '亲密关系', author: '罗兰·米勒', source: '当当网', rating: '9.0', year: '2023' },
  { title: '社会心理学', author: '戴维·迈尔斯', source: '京东', rating: '9.2', year: '2022' },
  { title: '影响力', author: '罗伯特·西奥迪尼', source: '豆瓣', rating: '8.9', year: '2024' },
];

// 当当网解析器
async function parseDangdang(html) {
  const books = [];
  const titleRegex = /<a[^>]*class="[^"]*tit[^"]*"[^>]*>([^<]+)<\/a>/gi;
  const authorRegex = /<a[^>]*class="[^"]*author[^"]*"[^>]*>([^<]+)<\/a>/gi;
  
  let titleMatch, authorMatch;
  while ((titleMatch = titleRegex.exec(html)) !== null) {
    const title = titleMatch[1].trim();
    authorRegex.lastIndex = titleMatch.index;
    authorMatch = authorRegex.exec(html);
    const author = authorMatch ? authorMatch[1].trim() : '未知作者';
    
    if (title && title.length > 2) {
      books.push({
        title,
        author,
        source: '当当网',
        zlibraryUrl: `https://z-lib.fm/s/?q=${encodeURIComponent(title)}`
      });
    }
  }
  return books;
}

// 豆瓣解析器
async function parseDouban(html) {
  const books = [];
  const itemRegex = /<li[^>]*class="[^"]*chart[^"]*"[^>]*>[\s\S]*?<a[^>]*title="([^"]+)"[^>]*>[\s\S]*?<span[^>]*class="author[^"]*"[^>]*>([^<]+)</gi;
  
  let match;
  while ((match = itemRegex.exec(html)) !== null) {
    const title = match[1].trim();
    const author = match[2].trim().replace('作者: ', '');
    
    books.push({
      title,
      author,
      source: '豆瓣',
      zlibraryUrl: `https://z-lib.fm/s/?q=${encodeURIComponent(title)}`
    });
  }
  return books;
}

// 京东解析器
async function parseJD(html) {
  const books = [];
  const itemRegex = /<em[^>]*>([^<]+)<\/em>[\s\S]*?<a[^>]*class="[^"]*p-name[^"]*"[^>]*>([^<]+)</gi;
  
  let match;
  while ((match = itemRegex.exec(html)) !== null) {
    const title = match[2].trim().replace(/<[^>]+>/g, '');
    const author = match[1].trim();
    
    books.push({
      title,
      author,
      source: '京东',
      zlibraryUrl: `https://z-lib.fm/s/?q=${encodeURIComponent(title)}`
    });
  }
  return books;
}

// 搜索书籍
async function searchBooks(query, env) {
  const useMock = env.USE_MOCK_DATA === 'true';
  let books = [];
  
  if (useMock) {
    books = MOCK_BOOKS;
  } else {
    // 从 KV 缓存获取
    try {
      const cached = await env.BOOKS_CACHE.get('books');
      if (cached) {
        books = JSON.parse(cached);
      }
    } catch (e) {
      console.error('KV read error:', e);
    }
  }
  
  // 搜索匹配
  if (!query || query.trim() === '') {
    return books.map(b => ({ ...b, matchScore: 100 }));
  }
  
  const searchTerms = query.toLowerCase().split(/\s+/);
  
  const scored = books.map(book => {
    const titleLower = book.title.toLowerCase();
    const authorLower = (book.author || '').toLowerCase();
    
    let score = 0;
    for (const term of searchTerms) {
      if (titleLower.includes(term)) score += 10;
      if (authorLower.includes(term)) score += 5;
    }
    
    return { ...book, matchScore: score };
  }).filter(b => b.matchScore > 0)
    .sort((a, b) => b.matchScore - a.matchScore);
  
  return scored;
}

// 抓取所有来源
async function fetchAllSources() {
  const allBooks = [];
  
  // 并行抓取（注意：生产环境需要处理 CORS 和反爬）
  const results = await Promise.allSettled([
    fetch('https://category.dangdang.com/pu1.54.00.00.00.00.html').then(r => r.text()).catch(() => ''),
    fetch('https://book.douban.com/chart').then(r => r.text()).catch(() => ''),
  ]);
  
  // 解析结果
  const [dangdangHtml, doubanHtml] = results;
  
  if (dangdangHtml.status === 'fulfilled') {
    const books = await parseDangdang(dangdangHtml.value);
    allBooks.push(...books);
  }
  
  if (doubanHtml.status === 'fulfilled') {
    const books = await parseDouban(doubanHtml.value);
    allBooks.push(...books);
  }
  
  return allBooks;
}

// HTML 响应
function htmlResponse(body, status = 200) {
  return new Response(body, {
    status,
    headers: {
      'Content-Type': 'text/html; charset=utf-8',
      'Access-Control-Allow-Origin': '*',
    }
  });
}

// JSON 响应
function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
    }
  });
}

// 路由处理
async function handleRequest(request, env) {
  const url = new URL(request.url);
  const path = url.pathname;
  
  // API: 搜索
  if (path === '/api/search' || path === '/search') {
    const query = url.searchParams.get('q') || url.searchParams.get('query') || '';
    const books = await searchBooks(query, env);
    return jsonResponse({
      success: true,
      query,
      total: books.length,
      books: books.slice(0, 50) // 限制返回数量
    });
  }
  
  // API: 刷新缓存
  if (path === '/api/refresh' || path === '/refresh') {
    const books = await fetchAllSources();
    
    if (!env.USE_MOCK_DATA && env.BOOKS_CACHE) {
      await env.BOOKS_CACHE.put('books', JSON.stringify(books));
      await env.BOOKS_CACHE.put('lastUpdate', new Date().toISOString());
    }
    
    return jsonResponse({
      success: true,
      total: books.length,
      updated: new Date().toISOString()
    });
  }
  
  // API: 获取全部书籍
  if (path === '/api/books' || path === '/books') {
    const books = await searchBooks('', env);
    return jsonResponse({
      success: true,
      total: books.length,
      books
    });
  }
  
  // API: 健康检查
  if (path === '/api/health' || path === '/health') {
    return jsonResponse({
      status: 'ok',
      timestamp: new Date().toISOString(),
      sources: Object.keys(BOOK_SOURCES)
    });
  }
  
  // 默认：返回前端页面
  return fetch(request);
}

export default {
  async fetch(request, env, ctx) {
    return handleRequest(request, env);
  }
};
