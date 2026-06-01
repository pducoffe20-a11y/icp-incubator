# CSV Schema

Expected columns:

| Column | Required | Notes |
|---|---:|---|
| `account_name` | yes | Organization name. |
| `contact_name` | no | Preferred recipient name. |
| `contact_title` | no | Buyer/persona clue. |
| `contact_email` | no | Required to draft. Missing email goes to Hold. |
| `website` | no | Used for research and validation. |
| `vertical` | no | Association, healthcare, banking, manufacturing, credentialing, CE, workforce, etc. |
| `state` | no | Useful for regional relevance. |
| `signal` | no | Why-now trigger. Specific evidence is strongest. |
| `priority` | no | Suggested values: high, med, low. |

Ready rows need a usable `account_name` and `contact_email`. Rows with no email are held unless enrichment is added later.
