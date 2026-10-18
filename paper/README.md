# Evidence-MAD IEEE paper draft

`main.tex` is an IEEE conference-style draft based on the 96 matched trace files copied into `../traces/` and the trace-derived summary in `../trace_derived_summary.json`. The literature review includes all 16 entries from the updated literature review presentation, with two additional references for RAG and NLI foundations. It has seven Matplotlib plots plus a separate Matplotlib architecture diagram. Every figure has a white background and black text.

The paper reports descriptive system behavior only. The matched trace bundle contains no gold answer labels, so it does not claim key-fact accuracy or conflict-detection precision/recall. It also discloses that recorded model identifiers vary between systems.

Build with `pdflatex main.tex`, `bibtex main`, then `pdflatex main.tex` twice in an environment with IEEEtran and BibTeX installed. No PDF was generated here because `pdflatex` is not installed in the current environment.
