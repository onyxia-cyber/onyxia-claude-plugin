---
name: inventory
description: >-
  Find, count, and inspect the tenant's devices and users, such as how many
  devices there are per OS, which laptops are unencrypted, which users lack
  MFA, or everything about one device or person.
metadata:
  tools:
    - inventory_breakdown
    - inventory_search
    - inventory_get
---

# Inventory

Each connected product reports its own record for a device or user. Onyxia merges
the records that describe the same device or person into one entity. Answer about
entities, never about the records of one product.

## Pick the tool by the question

| The user asks | Tool |
| --- | --- |
| How many there are per OS, type, department, location, or recency | `inventory_breakdown` |
| How many there are in total, or how many match a filter | `inventory_search`, read `total_results` |
| Which ones match a filter | `inventory_search` |
| Everything about one device or user | `inventory_get`, with an `ENTITY_ID` from a search |

- For a total, call `inventory_search` with `limit` 1 and read `total_results`.
  Never page through a search to count.
- Never add up breakdown counts to get a total. One entity can count in more
  than one bucket, and the recency buckets overlap: "Last 7 days" is inside
  "Last 30 days".
- The inventory has no history. For how a measure changed over time, such as
  MFA coverage or encryption, use the metrics skill.

## Before you query

- Always pass a recency window to `inventory_breakdown` as `last_days`. It counts
  the devices seen, or the users who logged in, within that many days. When the
  question names no time, use 30 days. When it names a time, such as "this
  week", use it, such as 7 days.

- Leave the window out only when the user asks for every device or user,
  whatever its age, or when you break down by LAST_SEEN or LAST_LOGIN.

- Use the same window in `inventory_search`, as `{"LAST_SEEN": {"last_days_": N}}`
  or `{"LAST_LOGIN": {"last_days_": N}}` in its `query_filter`, so the numbers
  agree.

- Take exact filter values from breakdown buckets or earlier results. A
  breakdown shows only the five most common values, so for another value, search
  first or filter with `contains_`. Text matching ignores case.

- To list the entities of a breakdown bucket, pass its `query_filter` to
  `inventory_search` as it is. To narrow the list, add columns to that filter.

## Reading results

- A filter matches an entity when any of its sources reports a matching value,
  not only its resolved value. When the difference matters, check the entity
  with `inventory_get`.
- A missing value is not "no". A device that no source reports encryption for is
  not unencrypted. Count those with `no_value_`, and name them separately.
- Sources can disagree about an entity, such as its OS. The entity shows one
  resolved value. When the disagreement matters, show each source's value from
  the attribute's `values` in `inventory_get`.
- The tools say when the tenant has no inventory for an entity type. That is not
  zero entities. Check `list_products` for a missing source or a failed sync.
- When a tool refuses a filter, the error names the problem, such as an unknown
  column. Correct the filter and try again.
- The inventory is rebuilt once a day. `last_updated` is when it was built. Say
  how fresh the data is when the user asks about something recent.

## Answering

Lead with the number or the list, and give the window in the same sentence. For
example: "Windows is the most common OS among devices seen in the last 30 days,
with 812 devices."

When you left the window out, say "all devices, whatever
their age". Show a breakdown or a search as a Markdown table, never as a list.
Describe the details of one entity in your text. End with one useful next
step, such as a filter that narrows the list.

## References

Load a reference when the question needs its detail:

- [references/devices.md](references/devices.md): device fields and filters,
  and encryption, management, compliance, and staleness questions.
- [references/users.md](references/users.md): user fields and filters, and MFA,
  admin, and inactive-user questions.
