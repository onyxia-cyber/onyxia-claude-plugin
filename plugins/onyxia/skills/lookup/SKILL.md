---
name: lookup
description: >-
  Use when the whole message is just a value and no question, such as an email
  address, an IP address, a device name, or a person's name. Find what the value
  belongs to and describe it.
metadata:
  tools:
    - inventory_breakdown
    - inventory_search
    - inventory_get
---

# Lookup

A message that is only a value means "tell me about this". Find what the value
belongs to in the inventory and describe it. Do not ask what the person wants to
know.

## What counts as a bare value

- The message is one value, perhaps with a few words that ask nothing, such as
  "check 10.20.31.7" or "dana@acme.com ?".
- A real question around the value, such as "who owns 10.20.31.7?" or "is
  dana@acme.com using MFA?", is not a lookup. Use the inventory skill and follow
  it.
- A metric name such as "CPI-013" is not a lookup. Use the metrics skill and
  follow it.
- Look up one value at a time. When the message holds several, look up the first
  and say so.

## Recognise the value

| The value looks like | Probably | Search |
| --- | --- | --- |
| Has an `@` | A person's email address | Users with `{"EMAILS_ADDRESSES": {"array_contains_": ["<email>"]}}` |
| Four numbers with dots, or hex groups with colons | An IP address | Devices with `{"IP_ADDRESSES": {"array_contains_": ["<ip>"]}}` |
| Six pairs of hex digits | A MAC address | Devices with `{"MAC_ADDRESSES": {"array_contains_": ["<mac>"]}}` |
| A short name with letters, digits and dashes, such as `LAPTOP-7F3K2` | A device name | Devices with `{"HOSTNAME": {"contains_": ["<name>"]}}` |
| Two or three capitalised words | A person's name | Users with `{"DISPLAY_NAME": {"contains_": ["<name>"]}}` |

- Search the value exactly as the person wrote it. Text matching ignores case.
- Sources write MAC addresses with colons or with dashes. When one form finds
  nothing, try the other before saying nothing matched.
- When the look of the value fits no row, or its row finds nothing and another
  row could fit, try the next likely row once.

## No time window

A lookup wants the thing whatever its age. Do not put LAST_SEEN or LAST_LOGIN in
the filter, and pass no `last_days`. This is the one place where the inventory
rule to always pass a window does not apply. Instead, say when each device was
last seen or each person last logged in, so the person can judge how stale it is.

## People are users only

For an email address or a person's name, search users only, not devices. The
answer is about the person's own record. Whether they own devices depends on what
the products report, so do not search for them. Offer the person's devices as the
next step instead.

## Three outcomes

**No match.** Say plainly that nothing in the inventory reports this value. Give
`last_updated` as when the inventory was last built. Offer one other value to
try, such as the device name for an IP address, or the exact spelling of a name.
Show no table.

**One match.** Fetch the full record with `inventory_get`. Describe it in text:
what it is, who it belongs to, and the security facts that matter.

- A device: OS, last seen, encrypted, managed, compliant, and which products
  report it.
- A person: department, last login, MFA, and admin or not. MFA is HAS_MFA.
  IS_STRONG is the password's strength, not MFA, so report it as its own fact.

**Several matches.** Show every match in one table, with the columns that tell
them apart: for devices, name, owner, OS, and last seen; for people, name, email
address, department, and last login. Read `total_results` and say how many
of the total are shown, such as "10 of 14". Do not pick one, and do not ask which
one before showing them. The same IP address often moves between devices over
time, so last seen is what tells them apart.

## Answering

Lead with what the value is in one sentence. For example: "10.20.31.7 is the
address of one device, Dana Levi's MacBook Pro, last seen yesterday."

Write yes or no facts in words, such as "MFA is on" or "the disk is not
encrypted", and a missing value as "no product reports it". Never show raw column
names or entity IDs. End with exactly one next step, such as naming the device
from the table to see it in full.
