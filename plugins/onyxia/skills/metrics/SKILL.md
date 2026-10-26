---
name: metrics
description: >-
  Answer how the tenant is doing on its security metrics (CPIs): the value now
  and whether it meets the SLA, how it changed over time, and the items behind
  it. Use for questions about an SLA, a target, a CPI such as "CPI-013", "how
  are we doing", or change over time, such as "Are we inside the SLA for
  encryption?", "How did MFA coverage change since July?", or "Which critical
  vulnerabilities are overdue?". For which devices or users, or how many there
  are now, use inventory.
metadata:
  tools:
    - search_metrics
    - get_metric_manifest
    - get_metric_latest
    - get_metric_timeseries
    - get_metric_records
---

# Metrics

A metric measures one security practice, such as the percent of overdue
vulnerabilities, and compares its value to an SLA.

## Pick the tool by the question

| The user asks | Tool |
| --- | --- |
| Which metrics exist, which the tenant uses, which it can turn on | `search_metrics` |
| What a metric measures, how it is calculated, which record columns can be filtered | `get_metric_manifest` |
| The value now, and whether it meets the SLA | `get_metric_latest` |
| How the value changed over a period | `get_metric_timeseries` |
| Which items are behind the value, and how many | `get_metric_records` |

## Metrics or inventory

Some topics are in both: encryption, managed devices, compliance, stale devices,
MFA, and inactive users. Choose by what the user wants, not by the topic.

- A target, an SLA, or change over time is a metric question. "Are we inside the
  SLA for encryption?" goes to CPI-091. "Did MFA coverage improve this quarter?"
  goes to CPI-043.
- Which devices or people, or how many there are now, is an inventory question,
  such as "Which laptops are unencrypted?" or "Does Dana have MFA?".
- When the user asks for both, use both skills and answer both parts. When
  the answer gives a metric count and an inventory count, always say in one
  sentence why the numbers differ: a metric counts what each product reports
  and compares it to an SLA, and the inventory merges the reports for the same
  device or person into one. Do not try to match the counts record by record.

## Choosing the metric

- A name such as "CPI-013" is the name the app shows, `display_name`. Match it
  there, never against the slug. Slugs are internal: the metric the app shows
  as CPI-013 has the slug `cpi008`, and no metric is shown as CPI-008. When no
  `display_name` matches, do not answer for the metric whose slug has the same
  number. Say that no metric has that name, and suggest the closest metrics.
  Never show a slug to the user.
- When the question names a topic, such as "how are we doing on
  vulnerabilities?", answer for the metrics the tenant uses in that topic: one
  table row each, with the value, the SLA and the verdict, then the main
  points.
- When the question names one measure, pick the metric that fits it best.
  When several fit, prefer one the tenant has turned on. Answer for it, then
  name the other close matches in one line.
- Ask which metric the user means only when nothing separates the matches, such
  as CPI-043 and CPI-044 for "our MFA number" when both are turned on.

## Answering

- Start with the value and the SLA verdict in one sentence. Name the metric by
  its app name and title, and give the section and the date. For example:
  "CPI-013 Percent of Overdue Vulnerabilities, critical section: 12% on
  October 9, inside the 15% SLA."
- For a trend, give a summary first: the start and end values, the highest and
  lowest, and when the SLA was missed. Show a table of the points only for
  weekly or monthly points, never for daily ones.
- Show records as a Markdown table, and say how many of the total you show,
  such as "25 of 140".
- End with one useful next step, not a choice of several, such as "I can
  show the overdue critical items."
