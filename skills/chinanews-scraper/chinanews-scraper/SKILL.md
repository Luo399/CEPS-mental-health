---
name: chinanews-scraper
description: 爬取中国新闻网滚动新闻，支持单页和多页数据爬取；当用户需要爬取新闻网数据、获取新闻列表、批量采集新闻信息时使用
dependency:
  python:
    - requests>=2.28.0
    - beautifulsoup4>=4.11.0
    - openpyxl>=3.0.0
---

# 中国新闻网爬虫

## 任务目标
- 本 Skill 用于：爬取中国新闻网滚动新闻频道的数据
- 能力包含：单页新闻爬取、多页批量爬取、JSON/Excel格式输出
- 触发条件：用户需要获取中国新闻网的新闻数据、批量采集新闻信息、分析新闻内容

## 前置准备
- 依赖说明：以下Python包已在依赖中配置
  ```
  requests>=2.28.0
  beautifulsoup4>=4.11.0
  openpyxl>=3.0.0
  ```
- 无需额外系统准备

## 操作步骤

### 标准流程

1. **确定爬取需求**
   - 评估需要爬取的页数范围
   - 确认数据输出格式（JSON或Excel）

2. **执行爬取脚本**
   - **单页爬取**：调用 `scripts/crawl_chinanews.py` 处理单页数据
     ```bash
     python scripts/crawl_chinanews.py --page 1
     ```
   - **多页爬取**：调用 `scripts/crawl_chinanews.py` 处理多页数据
     ```bash
     python scripts/crawl_chinanews.py --start-page 1 --end-page 5
     ```

3. **获取输出结果**
   - **JSON格式**（默认）：数据输出到标准输出，可直接保存为.json文件
   - **Excel格式**：数据自动保存为.xlsx文件，包含格式化的表格

4. **数据后处理**
   - 智能体根据用户需求对数据进行进一步处理
   - 可选操作：数据清洗、内容分析、统计汇总

### 可选分支
- 当 **爬取单页**时：使用 `--page` 参数指定页码
- 当 **爬取多页**时：使用 `--start-page` 和 `--end-page` 指定范围
- 当 **输出Excel格式**时：使用 `--output excel` 参数
- 当 **指定Excel文件名**时：使用 `--filename` 参数（默认chinanews_news.xlsx）
- 当 **需要自定义User-Agent**时：使用 `--user-agent` 参数（可选）

## 资源索引
- 必要脚本：见 [scripts/crawl_chinanews.py](scripts/crawl_chinanews.py)（用途：爬取中国新闻网数据，支持单页和多页模式）

## 注意事项
- 脚本已内置请求间隔，避免频繁请求
- 建议合理设置爬取页数，避免过度采集
- 支持JSON和Excel两种输出格式，默认为JSON
- Excel输出会自动生成格式化表格，包含表头样式
- 新闻链接为完整URL，可直接访问

## 使用示例

### 示例1：爬取单页新闻（JSON格式）
```bash
# 爬取第1页新闻，输出JSON格式
python scripts/crawl_chinanews.py --page 1
```
- 输出：第1页所有新闻的JSON数据

### 示例2：爬取多页新闻（JSON格式）
```bash
# 爬取第1页到第5页新闻，输出JSON格式
python scripts/crawl_chinanews.py --start-page 1 --end-page 5
```
- 输出：1-5页所有新闻的JSON数据

### 示例3：保存JSON到文件
```bash
# 爬取数据并保存为JSON文件
python scripts/crawl_chinanews.py --start-page 1 --end-page 3 > news_data.json
```
- 输出：数据保存到 news_data.json 文件

### 示例4：爬取单页新闻（Excel格式）
```bash
# 爬取第1页新闻，输出Excel格式
python scripts/crawl_chinanews.py --page 1 --output excel
```
- 输出：生成 chinanews_news.xlsx 文件

### 示例5：爬取多页新闻（Excel格式，自定义文件名）
```bash
# 爬取1-5页新闻，输出Excel格式，指定文件名
python scripts/crawl_chinanews.py --start-page 1 --end-page 5 --output excel --filename my_news.xlsx
```
- 输出：生成 my_news.xlsx 文件

### 示例6：智能体处理数据
```python
# 智能体读取并处理JSON数据
import json

data = json.loads(output)
for item in data:
    print(f"{item['category']}: {item['title']}")
```
- 输出：按栏目分类的新闻标题列表
