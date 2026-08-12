# Quotable sentences (可引用句筛选标准)

This reference provides detailed rules for selecting and formatting verbatim quotable sentences, covering dimension 8 (可引用句).

## Selection criteria

### Priority order (select from top)

1. **Theoretical framework definitions**: sentences that define key concepts, theoretical mechanisms, or causal logic
   - Good: "We define digital transformation as the integration of digital technology into all areas of a business, fundamentally changing how it operates and delivers value to customers."
   - Bad: "Digital transformation has become an important topic in recent years."

2. **Core mechanism articulation**: sentences that explain the causal pathway or mediating mechanism
   - Good: "The mechanism through which environmental regulation affects firm innovation operates through two channels: the compliance cost effect and the Porter hypothesis effect."
   - Bad: "Table 3 shows the mechanism test results."

3. **Research contribution statements**: sentences that clearly articulate what the paper contributes
   - Good: "This paper contributes to the literature by providing the first causal evidence of the effect of X on Y using a quasi-natural experiment."
   - Bad: "Our findings have important implications."

4. **Methodological justification**: sentences that explain why a specific identification strategy is valid
   - Good: "The staggered DID design exploits the exogenous variation in policy implementation timing across provinces, which satisfies the parallel trends assumption as shown in Figure 2."
   - Bad: "We use DID in this paper."

### What NOT to select

- Pure data descriptions: "The sample covers 10,000 firms from 2010 to 2020."
- Simple table/figure recaps: "Column (1) shows the baseline results."
- Generic academic filler: "The results are robust to alternative specifications."
- Sentences that are too long to be quoted (over 50 words)
- Sentences with many inline citations that would be confusing out of context

## Citation format

Each quotable sentence must include:

```html
<div class="quote-item">
  "[verbatim English sentence from original]"
  <span class="quote-ref">— [First Author Surname] et al. ([Year]), p. [page number]</span>
</div>
```

### Format rules

- Author: use first author's surname only + "et al." for 3+ authors, or "and [Second Author]" for 2 authors
- Year: publication year in parentheses
- Page: exact page number from the PDF
- Language: keep the original English text verbatim, do not translate into Chinese
- If the user's paper is in Chinese and they want Chinese translations alongside, add a `（中文翻译：...）` after the English quote

### Page number annotation

- If the PDF has clear page numbers, use the exact page
- If page numbers are unclear, use the section name: "p. [Introduction 部分]"
- If the sentence spans two pages, use the starting page
- For papers without page numbers (online-first): use "p. [Section X]" or "p. [无页码]"

## Quantity

- **Per paper**: 2-3 sentences
- **Prioritize quality over quantity**: one excellent quotable sentence is better than three mediocre ones
- If the paper genuinely has more than 3 highly quotable sentences, select the 3 most useful for the user's specific research context (as determined by dimension 7 fit assessment)

## Integration with dimension 7

When possible, select quotable sentences that align with the fit assessment:
- If dimension 7 says the paper supports hypothesis 2 about mechanism X, prioritize quotable sentences about mechanism X
- If dimension 7 says the paper's methodology is replicable, prioritize the identification strategy justification sentence
- This ensures dimension 8's quotable sentences are immediately actionable for the user's writing
