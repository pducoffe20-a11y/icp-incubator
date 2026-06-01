# Step 0 — Intake

Load the CSV. Validate required headers. Normalize whitespace, account names, and lowercase emails. Split rows into Ready and Hold.

Ready = account name plus usable contact email. Hold = missing email, broken row, or impossible recipient.

Output: Ready count, Hold count, and hold reasons.
