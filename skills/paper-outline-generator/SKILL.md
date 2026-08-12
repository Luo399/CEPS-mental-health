---
name: paper-outline-generator
description: Generate comprehensive, structured paper outlines for academic papers, research proposals, theses, and dissertations. Use this skill when the user needs to create a detailed outline for any type of academic writing, including research papers, literature reviews, conference papers, grant proposals, or thesis/dissertation chapters. This skill provides discipline-specific templates, standard academic structures (IMRAD, PRISMA, etc.), and detailed section breakdowns with key points and research questions.
allowed-tools: Read Write Edit Bash
license: MIT license
metadata:
    skill-author: Academic Writing Assistant
---

# Paper Outline Generator

## Overview

**Paper Outline Generator** is a specialized skill for creating comprehensive, structured outlines for academic papers, research proposals, theses, and dissertations. This skill helps researchers and students organize their ideas into a logical framework before writing, ensuring all necessary components are included and properly structured.

The skill provides discipline-specific templates, standard academic structures (IMRAD, PRISMA, etc.), and detailed section breakdowns with key points, research questions, and methodological considerations.

## When to Use This Skill

**ALWAYS use this skill when the user mentions any of the following:**

- Creating a paper outline, research outline, or thesis outline
- Structuring an academic paper, research proposal, or dissertation
- Planning a literature review, systematic review, or meta-analysis
- Developing a research methodology or study design
- Organizing ideas for a conference paper or journal submission
- Writing a grant proposal or research funding application
- Preparing a thesis or dissertation chapter outline
- Any request related to academic writing structure or organization

**This skill is particularly useful for:**

- Graduate students writing theses or dissertations
- Researchers preparing journal submissions
- Academics developing research proposals
- Students organizing term papers or research projects
- Anyone needing structured guidance for academic writing

## Core Principles

1. **Structure First**: Always create a detailed outline before writing
2. **Discipline-Specific**: Adapt outlines to the conventions of specific academic fields
3. **Comprehensive Coverage**: Ensure all necessary sections are included
4. **Logical Flow**: Create outlines with clear progression of ideas
5. **Actionable Details**: Include specific research questions, hypotheses, and methodological considerations

## Outline Generation Process

### Step 1: Gather Requirements
- Ask the user about their paper type, discipline, and specific requirements
- Determine the appropriate structure (IMRAD, PRISMA, etc.)
- Identify the target audience and publication venue (if applicable)

### Step 2: Select Template
Choose from the following template categories:

#### Research Paper Templates
- **Standard IMRAD**: Introduction, Methods, Results, and Discussion
- **Extended IMRAD**: Abstract, Introduction, Methods, Results, Discussion, Conclusion, References
- **Conference Paper**: Abstract, Introduction, Related Work, Methodology, Results, Discussion, Conclusion, References
- **Short Paper**: Abstract, Introduction, Methodology, Results, Discussion, References

#### Literature Review Templates
- **Traditional Review**: Introduction, Search Strategy, Thematic Analysis, Synthesis, Conclusion
- **Systematic Review (PRISMA)**: Abstract, Introduction, Methods, Results, Discussion, Conclusion
- **Meta-Analysis**: Abstract, Introduction, Methods, Results, Discussion, Conclusion
- **Scoping Review**: Introduction, Objectives, Inclusion Criteria, Search Strategy, Data Extraction, Results, Discussion, Conclusion

#### Thesis/Dissertation Templates
- **PhD Dissertation**: Title Page, Abstract, Table of Contents, List of Figures/Tables, Chapters 1-5+, References, Appendices
- **Master's Thesis**: Abstract, Introduction, Literature Review, Methodology, Results, Discussion, Conclusion, References
- **Undergraduate Thesis**: Abstract, Introduction, Literature Review, Methodology, Results, Discussion, Conclusion, References

#### Proposal Templates
- **Research Proposal**: Title, Abstract, Introduction, Literature Review, Research Questions, Methodology, Timeline, Budget, References
- **Grant Proposal**: Abstract, Specific Aims, Background/Significance, Preliminary Studies, Research Design, Timeline, Budget, References
- **PhD Proposal**: Introduction, Literature Review, Research Gap, Research Questions, Methodology, Expected Contributions, Timeline, References

### Step 3: Generate Detailed Outline
For each section, provide:
- **Section Title**: Clear, descriptive title
- **Purpose**: What this section should accomplish
- **Key Points**: 3-5 main points to cover
- **Research Questions**: Specific questions to address (where applicable)
- **Methodological Considerations**: How to approach this section
- **Expected Length**: Approximate word count or page range
- **Common Pitfalls**: What to avoid in this section

### Step 4: Customize for Discipline
Adapt the outline based on academic discipline:

#### Natural Sciences
- Emphasis on hypothesis testing, experimental design, statistical analysis
- Include sections for materials, procedures, data analysis
- Follow journal-specific formatting requirements

#### Social Sciences
- Emphasis on theoretical frameworks, methodology, ethical considerations
- Include sections for conceptual framework, sampling, data collection methods
- Address positionality and reflexivity where appropriate

#### Humanities
- Emphasis on argumentation, close reading, theoretical perspectives
- Include sections for historical context, primary source analysis, theoretical framework
- Focus on narrative structure and rhetorical strategies

#### Engineering & Technology
- Emphasis on problem statement, solution design, implementation, evaluation
- Include sections for system architecture, algorithms, performance metrics
- Follow IEEE or ACM formatting standards

#### Medical & Health Sciences
- Emphasis on study design, patient population, interventions, outcomes
- Include sections for ethics approval, consent procedures, statistical methods
- Follow CONSORT, STROBE, or PRISMA guidelines as appropriate

### Step 5: Provide Writing Guidance
For each section, offer specific writing advice:
- **Introduction**: Start broad, narrow to specific research gap, state objectives
- **Literature Review**: Thematic organization, critical analysis, identify gaps
- **Methodology**: Detailed enough for replication, justify choices
- **Results**: Objective presentation, use tables/figures appropriately
- **Discussion**: Interpret results, compare with literature, acknowledge limitations
- **Conclusion**: Summarize key findings, state implications, suggest future research

## Output Format

**ALWAYS present outlines in this exact format:**

```
# [Paper Title] - Comprehensive Outline

## Paper Information
- **Type**: [Research Paper/Literature Review/Thesis/etc.]
- **Discipline**: [Field/Discipline]
- **Target Audience**: [Academic Level/Publication Venue]
- **Estimated Length**: [Word Count/Page Range]

## Overall Structure
[Brief description of the chosen template and rationale]

## Detailed Section Breakdown

### 1. [Section Title]
**Purpose**: [What this section should accomplish]
**Key Points**:
1. [Point 1]
2. [Point 2]
3. [Point 3]
**Research Questions**:
- [Question 1]
- [Question 2]
**Methodological Considerations**: [How to approach this section]
**Expected Length**: [Word count or pages]
**Common Pitfalls to Avoid**: [What to watch out for]

### 2. [Next Section Title]
[Continue with same structure...]

## Writing Timeline & Milestones
- Week 1-2: [Tasks for first phase]
- Week 3-4: [Tasks for second phase]
- Week 5-6: [Tasks for third phase]
- Week 7-8: [Final polishing and submission]

## Additional Resources
- [Relevant style guides]
- [Recommended software/tools]
- [Key references for methodology]
```

## Examples of Good Outlines

### Example 1: Social Science Research Paper
```
# The Impact of Social Media on Political Polarization - Comprehensive Outline

## Paper Information
- **Type**: Empirical Research Paper
- **Discipline**: Political Science/Sociology
- **Target Audience**: Journal of Communication
- **Estimated Length**: 8,000 words

## Overall Structure
Standard IMRAD structure with extended literature review and methodology sections, appropriate for communication studies.

## Detailed Section Breakdown

### 1. Abstract (250 words)
**Purpose**: Concise summary of entire paper
**Key Points**:
1. Research problem and significance
2. Methodology and sample
3. Key findings
4. Main conclusions and implications
...
```

### Example 2: STEM Literature Review
```
# Machine Learning Applications in Medical Imaging - Comprehensive Outline

## Paper Information
- **Type**: Systematic Literature Review
- **Discipline**: Computer Science/Medical Informatics
- **Target Audience**: IEEE Transactions on Medical Imaging
- **Estimated Length**: 10,000 words

## Overall Structure
PRISMA-guided systematic review structure with emphasis on methodology transparency and comprehensive synthesis.

## Detailed Section Breakdown

### 1. Abstract (300 words)
**Purpose**: Structured abstract following journal requirements
**Key Points**:
1. Background and objectives
2. Search strategy and selection criteria
3. Main results and findings
4. Conclusions and clinical implications
...
```

## Common Variations & Adaptations

### For Different Paper Lengths
- **Short Papers (2,000-4,000 words)**: Focus on essential sections, combine discussion and conclusion
- **Medium Papers (5,000-8,000 words)**: Standard structure with moderate detail
- **Long Papers (10,000+ words)**: Extended sections, multiple sub-sections, comprehensive literature review

### For Different Academic Levels
- **Undergraduate**: More guidance, simpler structure, emphasis on learning objectives
- **Master's**: Intermediate complexity, methodological rigor expected
- **PhD/Research**: Highest complexity, theoretical depth, methodological sophistication

### For Different Publication Venues
- **Journal Articles**: Follow specific journal guidelines, emphasize novelty
- **Conference Papers**: Emphasize timeliness, concise presentation
- **Book Chapters**: Thematic focus, comprehensive coverage
- **Theses/Dissertations**: Extended format, multiple chapters

## Quality Checklist

Before finalizing any outline, verify:

1. **Logical Flow**: Does the outline progress logically from introduction to conclusion?
2. **Completeness**: Are all necessary sections included for the paper type?
3. **Discipline Appropriateness**: Does the structure match field conventions?
4. **Actionable Detail**: Are sections specific enough to guide writing?
5. **Research Alignment**: Do research questions align with methodology?
6. **Audience Consideration**: Is the structure appropriate for the target audience?
7. **Practicality**: Is the timeline realistic for the user's constraints?

## Integration with Other Skills

This skill works well with:
- **research-lookup**: For literature review sections
- **scientific-writing**: For converting outlines to full text
- **citation-management**: For reference sections
- **statistical-analysis**: For methodology and results sections

## Troubleshooting

### If the user is unsure about structure:
- Provide 2-3 alternative structures with pros and cons
- Suggest looking at examples from target publication venues
- Recommend consulting with advisors or colleagues

### If the outline seems too complex:
- Simplify to core sections first
- Add detail in subsequent iterations
- Focus on the most critical components

### If discipline conventions conflict:
- Research specific journal or department guidelines
- Consult field-specific style manuals
- Balance innovation with convention

## Final Notes

Remember: A good outline is the foundation of successful academic writing. It should be detailed enough to guide the writing process but flexible enough to accommodate new insights. Always encourage users to revisit and revise their outlines as their research evolves.

**Key Success Factors:**
1. Start with clear research questions
2. Match structure to purpose and audience
3. Include sufficient methodological detail
4. Plan for iterative refinement
5. Align with disciplinary norms