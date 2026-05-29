llm-jailbreak-safety-demo/
│
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── configs/
│   ├── model_config.yaml
│   ├── dataset_config.yaml
│   ├── defense_config.yaml
│   └── experiment_config.yaml
│
├── data/
│   ├── raw/
│   │   └── sample_prompts.csv
│   ├── processed/
│   │   └── evaluation_prompts.csv
│   └── results/
│       ├── baseline_results.csv
│       ├── defense_results.csv
│       └── summary_metrics.csv
│
├── src/
│   ├── __init__.py
│   │
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── base_client.py
│   │   ├── openai_client.py
│   │   ├── local_client.py
│   │   └── mock_client.py
│   │
│   ├── datasets/
│   │   ├── __init__.py
│   │   ├── loader.py
│   │   └── preprocessing.py
│   │
│   ├── attacks/
│   │   ├── __init__.py
│   │   ├── prompt_variants.py
│   │   └── benign_stress_tests.py
│   │
│   ├── defenses/
│   │   ├── __init__.py
│   │   ├── input_filter.py
│   │   ├── output_filter.py
│   │   ├── safety_prompt.py
│   │   └── refusal_classifier.py
│   │
│   ├── evaluation/
│   │   ├── __init__.py
│   │   ├── evaluator.py
│   │   ├── metrics.py
│   │   └── judge.py
│   │
│   ├── visualization/
│   │   ├── __init__.py
│   │   ├── plot_metrics.py
│   │   └── report_tables.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logger.py
│       ├── seed.py
│       └── io.py
│
├── scripts/
│   ├── 01_prepare_dataset.py
│   ├── 02_run_baseline_eval.py
│   ├── 03_run_defense_eval.py
│   ├── 04_compare_results.py
│   └── 05_generate_figures.py
│
├── notebooks/
│   ├── 01_dataset_exploration.ipynb
│   ├── 02_baseline_evaluation.ipynb
│   ├── 03_defense_comparison.ipynb
│   └── 04_final_analysis.ipynb
│
├── app/
│   ├── streamlit_app.py
│   └── assets/
│       └── screenshots/
│
├── tests/
│   ├── test_dataset_loader.py
│   ├── test_defenses.py
│   ├── test_metrics.py
│   └── test_mock_client.py
│
├── reports/
│   ├── latex/
│   │   ├── main.tex
│   │   ├── sections/
│   │   │   ├── 01_introduction.tex
│   │   │   ├── 02_background.tex
│   │   │   ├── 03_tutorial_content.tex
│   │   │   ├── 04_experiments.tex
│   │   │   ├── 05_discussion.tex
│   │   │   └── 06_demo_description.tex
│   │   ├── figures/
│   │   └── references.bib
│   │
│   └── final_report.pdf
│
├── slides/
│   ├── presentation.pptx
│   └── figures/
│
└── artifacts/
    ├── trained_classifiers/
    ├── logs/
    └── demo_video_link.txt