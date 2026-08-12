# Scientific Writing Project Structure

```
scientific-writing/
├── project_structure.md          # This file
├── README.md                    # Project overview and instructions
├── latex/
│   ├── main.tex                # Main LaTeX document
│   ├── sections/               # Individual sections
│   │   ├── introduction.tex
│   │   ├── methodology.tex
│   │   ├── results.tex
│   │   ├── discussion.tex
│   │   └── conclusion.tex
│   ├── figures/                # Images and graphics
│   ├── tables/                 # Tables
│   ├── references.bib         # Bibliography database
│   └── config/                # Configuration files
│       ├── packages.tex       # Custom package imports
│       └── commands.tex       # Custom commands
├── drafts/
│   ├── draft1.tex             # First draft
│   ├── draft2.tex             # Second draft
│   └── notes/                 # Draft notes
├── data/
│   ├── raw/                   # Raw data
│   └── processed/             # Processed data
├── scripts/                   # Analysis and visualization scripts
├── references/                # Reference materials
└── output/
    ├── pdfs/                  # Generated PDFs
    └── submissions/           # Submitted manuscripts
```

## Getting Started

1. Edit `README.md` to set up your project information
2. Configure the LaTeX files in `latex/config/`
3. Start writing in `latex/sections/`
4. Track drafts in the `drafts/` directory
5. Store data and analysis in appropriate subdirectories
6. Generate PDFs in the `output/` directory