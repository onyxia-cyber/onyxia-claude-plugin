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
| Everything about one device or user | `inventory_search` to find it, then `inventory_get` with its `ENTITY_ID` |

- For a total, call `inventory_search` with `limit` 1 and read `total_results`.
  Never page through a search to count.
- Never add up breakdown counts to get a total. One entity can count in more
  than one bucket, and the recency buckets overlap: "Last 7 days" is inside
  "Last 30 days".
- The inventory has no history. For how a measure changed over time, such as
  MFA coverage or encryption, use the metrics skill.

## Time window

A question about a group of devices or users gets a recency window. A search for
one device or person gets none, as the search workflow below says.

- For a group, always pass a recency window to `inventory_breakdown` as
  `last_days`. It counts the devices seen, or the users who logged in, within
  that many days. When the question names no time, use 30 days. When it names a
  time, such as "this week", use it, such as 7 days.
- Use the same window in `inventory_search`, as `{"LAST_SEEN": {"last_days_": N}}`
  or `{"LAST_LOGIN": {"last_days_": N}}` in its `query_filter`, so the numbers
  agree.
- Leave the window out when the user asks for every device or user, whatever its
  age, or when you break down by LAST_SEEN or LAST_LOGIN.
- When the user's own condition is about recency, such as users with no login in
  90 days, that condition replaces the default window. Do not add 30 days to it.

## Search workflow

Follow these steps for every search, whether it counts, lists, or finds one
device or person. The lookup skill follows them too.

### 1. Decide what the search is for

- **One device or person**, named by a value such as an email address, an IP
  address, or a device name. Search for that value only. Add no LAST_SEEN or
  LAST_LOGIN condition unless the user asks for one, because an old record is
  still the answer. Say when it was last seen or last logged in instead.
- **A group**, such as unencrypted laptops or one person's devices. Use the time
  window above, and add each condition the user names.

### 2. Match the value

- A complete identifier, such as a full email address, IP address, MAC address,
  serial number, or device name: use an exact filter. That is `array_contains_`
  for a list column and `any_` for a text column. The references name the column
  for each kind of value.
- Part of a value, or a person's name: match part of it with `contains_` or
  `array_like_`. When you do not know which column holds the value, use the
  free-text `search` instead of a filter.
- When an exact filter finds nothing and products may write the value
  differently, such as a device name with its domain, try partial matching once.
- Filter only on values the user gave or a result returned. Never guess an
  identifier, a domain, or a filter value. For a group, take values such as an
  OS or a department from breakdown buckets or earlier results. A breakdown shows
  only the five most common values, so for another value, search first or filter
  with `contains_`.
- To list the entities of a breakdown bucket, pass its `query_filter` to
  `inventory_search` as it is. To narrow the list, add columns to that filter.

### 3. Read the count

`total_results` counts every match, not only the records on the page. A page that
holds one record can be one of many.

- **0.** Nothing matches. Only a search that succeeded and counted 0 means this.
- **1.** One match. When the user asked about one device or person, fetch its
  full record with `inventory_get`, using the `ENTITY_ID` from that search.
- **More than 1.** Show the matches in a table, with the columns that tell them
  apart, and say how many of the total you show, such as "10 of 14". Do not pick
  one as the answer.

### 4. When a call does not succeed

- **No inventory.** The tool says the tenant has no inventory for that type. That
  is not zero entities. Say the inventory is missing, and check `list_products`
  for a missing source or a failed sync.
- **A problem with the request.** The error names it, such as an unknown column
  or a predicate the column does not take. Correct the request and try again.
- **A failed response.** The tool failed without naming a problem with the
  request, or its response could not be read, such as a response that does not
  match the tool's format. You do not know what matched. Say the search could not
  be completed, never that nothing matched. Do not repeat it, and do not change
  the filter, the columns, or the entity type to get around it.
- **Full details fail.** When `inventory_get` fails after a search succeeded,
  answer only with what the search returned, and say the full details could not
  be fetched.

## Reading results

- A filter matches an entity when any of its sources reports a matching value,
  not only its resolved value. When the difference matters, check the entity
  with `inventory_get`.
- A missing value is not "no". A device that no source reports encryption for is
  not unencrypted. Count those with `no_value_`, and name them separately.
- Sources can disagree about an entity, such as its OS. The entity shows one
  resolved value. When the disagreement matters, show each source's value from
  the attribute's `values` in `inventory_get`.
- The inventory is rebuilt once a day. `last_updated` is when it was built. Say
  how fresh the data is when the user asks about something recent.

## Answering

Lead with the number or the list, and give the window in the same sentence. For
example: "Windows is the most common OS among devices seen in the last 30 days,
with 812 devices."

When you left the window out of a group, say "all devices, whatever their age".
For one device or person, say when it was last seen or last logged in. Show a
breakdown or a search as a Markdown table, never as a list. Describe the details
of one entity in your text. When a call failed, say what you could not check.
End with one useful next step, such as a filter that narrows the list.

## References

Load a reference when the question needs its detail:

- [references/devices.md](references/devices.md): device fields and filters,
  and encryption, management, compliance, and staleness questions.
- [references/users.md](references/users.md): user fields and filters, and MFA,
  admin, and inactive-user questions.
