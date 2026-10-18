# Matched-result analysis (96 questions)

This folder preserves the 96 question traces shared by all six system configurations and includes seven Matplotlib plots (PNG and PDF) plus a trace-derived JSON summary. The accompanying `paper/` folder contains the IEEE LaTeX draft, citations, bibliography, and seven plots plus a black-text, white-background architecture diagram.

## What the plots show

- Debate activation by configuration.
- Evidence-decision state counts.
- Median and 95th-percentile end-to-end latency.
- Mean successful and failed model calls per question.
- Mean usable retrieval agents and retrieved claims per question.
- Debate outcomes (completed, partial, failed, or not triggered).
- Model identifiers recorded in the traces, showing the run's model-metadata mixture.

## Interpretation limits

The six folders contain matching questions, but the trace files do not provide gold answer labels for this 96-question set. The saved metrics mark key-fact accuracy as unscored (zero scored samples); these zeros must not be interpreted as 0% accuracy. Accordingly, this analysis reports operational behavior only and makes no accuracy or superiority claim. Latencies and call outcomes are single-run observations.

All result plots use white backgrounds and black text. The source data are copied under `traces/`; `analysis/generate_plots.py` regenerates those plots. `architecture/generate_architecture.py` regenerates the system architecture figure.
