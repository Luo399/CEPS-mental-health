# OpenAlex API

OpenAlex是一个开放的学术数据库，提供免费访问学术文献元数据。

## 基本信息

- **API Endpoint**: https://api.openalex.org
- **认证**: 无需API密钥
- **速率限制**: 每秒100次请求

## 主要端点

### /works

获取学术作品信息。

**请求示例**:
```bash
GET https://api.openalex.org/works?filter=from_publication_date:2021-01-01,to_publication_date:2024-12-31&search=machine+learning&sort=cited_by_count:desc
```

**参数**:
- `filter`: 过滤条件
- `search`: 搜索关键词
- `sort`: 排序方式
- `per_page`: 每页结果数
- `page`: 页码

## 文档

详细文档: https://docs.openalex.org/
