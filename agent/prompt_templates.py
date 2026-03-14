REPORT_SUMMARY_PROMPT = """
You are a quantitative research assistant.

Please write a clean strategy research summary based on the following inputs:

Strategy Name:
{strategy_name}

Symbol:
{symbol}

Metrics Summary:
{metrics_summary}

Trade Stats Summary:
{trade_stats_summary}

Decision Summary:
{decision_summary}

Strengths:
{strengths}

Weaknesses:
{weaknesses}

Next-Step Suggestions:
{next_step_suggestions}

Write the summary in a structured and concise format that is suitable for a research log.
""".strip()
