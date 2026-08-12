# Source: DOI, arXiv ID, or publisher URL

The user provided a DOI (e.g. `10.1038/s41586-026-10452-4`), an arXiv ID (e.g. `2301.07041`), or a publisher URL instead of a local file.

## Resolution strategy

### Step 1: Identify the identifier type

- **DOI**: starts with `10.` followed by registrant code
- **arXiv**: starts with digits + period (e.g. `2301.07041`) or contains `arxiv.org`
- **URL**: any other URL (publisher page, SSRN, RePEc, etc.)

### Step 2: Resolve to obtainable content

Use WebSearch and WebFetch to retrieve the paper:

1. **For DOI**: search `doi.org/[DOI]` to find the publisher page, then attempt to access the full text.
2. **For arXiv**: fetch from `arxiv.org/abs/[ID]` for metadata, then `arxiv.org/pdf/[ID]` for the full PDF.
3. **For publisher URL**: fetch the page to get abstract and metadata; check if full text PDF is accessible.
4. **For SSRN/RePEc**: fetch the abstract page; full text may require download.

### Step 3: Extract what is available

- **Full text obtained**: proceed with standard pdf-text extraction rules.
- **Only abstract + metadata**: generate a limited report. Fill dimensions 1 (研究问题) and 2 (核心假设) from the abstract. Mark dimensions 3-6 as "信息不足：仅获取到摘要". Attempt dimension 7 (适配性) based on abstract content. Skip dimension 8 or note limited availability.
- **Nothing obtained**: inform the user that the source could not be resolved and suggest providing a local PDF file.

## Reporting limitations

When full text is not available, add a note to the HTML report:

```html
<div class="disclaimer" style="background: #e6f7ff; border-color: #91d5ff;">
  <strong>来源提示：</strong>本文仅通过 [DOI/URL] 获取到摘要和元数据，完整全文未能获取。
  部分维度标注为"信息不足"，建议获取全文后重新精读以获得完整报告。
</div>
```

## Metadata extraction

Even with limited access, extract and display:
- Full paper title
- Author(s)
- Journal/venue
- Publication year
- DOI or URL
- Abstract text (verbatim)
