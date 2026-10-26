# Devices

A device's recency is LAST_SEEN, the latest time any source saw it. Devices break
down by OS_NAME, ASSET_TYPE, or LAST_SEEN.

| Question | Filter |
| --- | --- |
| Unencrypted devices | `{"IS_ENCRYPTED": {"equal_": false}}` |
| Unmanaged devices | `{"IS_MANAGED": {"equal_": false}}` |
| Non-compliant devices | `{"IS_COMPLIANCE": {"equal_": false}}` |
| Unsupervised devices | `{"IS_SUPERVISED": {"equal_": false}}` |
| Devices without cloud backup | `{"HAS_CLOUD_BACKUP": {"equal_": false}}` |
| Devices stale for 30 days or more | `{"STALE_TIME": {"gte_": 30}}` |
| Devices not seen in the last 90 days | `{"LAST_SEEN": {"lte_": "<the day 90 days ago>T23:59:59"}}` |
| Devices of one OS | `{"OS_NAME": {"any_": ["<value from a breakdown>"]}}` |
| One person's devices | `{"EMAIL_ADDRESS": {"any_": ["<email>"]}}` or `{"USER_NAMES": {"array_contains_": ["<name>"]}}` |
| Devices from one product | `{"SOURCES": {"any_": ["<product name>"]}}` |
| The device with one IP address | `{"IP_ADDRESSES": {"array_contains_": ["<ip>"]}}` |
| The device with one MAC address | `{"MAC_ADDRESSES": {"array_contains_": ["<mac>"]}}` |
| A device by name | `{"HOSTNAME": {"contains_": ["<name>"]}}` |

- STALE_TIME is a number of days. Filter it with `gte_`, `lte_`, or `between_`.
- USER_NAMES, GROUP_NAMES, GROUP_IDS, MAC_ADDRESSES and IP_ADDRESSES are lists.
  Filter them with `array_contains_` for an exact element, or `array_like_` for
  part of one.
- A device with no encryption value is one no source reports encryption for. It
  is not unencrypted. Count those separately with
  `{"IS_ENCRYPTED": {"no_value_": true}}`. The same holds for the other status
  fields.
- `equal_: false` finds a device when any source reports it as not encrypted,
  even when the resolved value is encrypted.
