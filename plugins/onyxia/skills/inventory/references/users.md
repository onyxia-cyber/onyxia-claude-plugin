# Users

A user's recency is LAST_LOGIN, the latest login any source reports. Users break
down by EMAIL_DOMAIN, DEPARTMENTS, LOCATION, GROUP_NAMES, or LAST_LOGIN.

| Question | Filter |
| --- | --- |
| Users without MFA | `{"HAS_MFA": {"equal_": false}}` |
| Users who can bypass MFA | `{"IS_BYPASS": {"equal_": true}}` |
| Users with a weak password | `{"IS_STRONG": {"equal_": false}}` |
| Admins | `{"ADMIN_STATUS": {"any_": ["isAdmin"]}}` |
| Inactive users, no login in 90 days | `{"LAST_LOGIN": {"lte_": "<the day 90 days ago>T23:59:59"}}` |
| Old passwords, not changed in a year | `{"PASSWORD_LAST_UPDATED": {"lte_": "<the day a year ago>T23:59:59"}}` |
| Users created in the last 30 days | `{"USER_CREATION_DATE": {"last_days_": 30}}` |
| Disabled or suspended accounts | `{"USER_STATUS": {"any_": ["<value from results>"]}}` |
| Users of one department | `{"DEPARTMENTS": {"array_contains_": ["<value from a breakdown>"]}}` |
| One person by email | `{"EMAILS_ADDRESSES": {"array_contains_": ["<email>"]}}` |
| One person by name | `{"DISPLAY_NAME": {"contains_": ["<name>"]}}` |

- DISPLAY_NAME is the person's full name. FIRST_NAME and LAST_NAME hold its
  parts and take the same predicates.
- ADMIN_STATUS holds isAdmin or nonAdmin. USER_STATUS values depend on the
  source, so take them from earlier results.
- EMAILS_ADDRESSES, DEPARTMENTS, GROUP_NAMES, USER_ROLES and EMAIL_DOMAIN are
  lists. A person can hold several of each. `array_contains_` matches any
  element, not only the first. Use `array_like_` for part of an element.
- Date fields take `gte_`, `lte_`, `between_` and `last_days_` only. A user with
  no LAST_LOGIN falls outside every date filter, so it is in no login count.
- A user with no MFA value is one no source reports MFA for. It is not a user
  without MFA. Count those separately with `{"HAS_MFA": {"no_value_": true}}`.
- `equal_: false` finds a user when any source reports no MFA, even when the
  resolved value is true.
