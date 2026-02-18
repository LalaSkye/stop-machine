# ALVIANTECH COMMS CENTER v0.1

> **Status:** ACTIVE
> **Created:** 2026-02-18T09:20:00Z
> **Owner:** HUMAN (LalaSkye)
> **Protocol version:** ENVELOPE v0.1 + R0 patch

---

## 1. PURPOSE

This file is the canonical communications postbox for the AlvianTech
project. All protocol messages between HUMAN and AI agents (TRINITY,
MORPHEUS, or any future named agent) are logged here as append-only
entries.

**Why this file exists:**
- The Hugging Face Space UI injects external S3 links into content,
  violating transport neutrality.
- A Git-hosted markdown file preserves raw text exactly as authored.
- Git's commit history provides an immutable, timestamped audit trail.

---

## 2. PROTOCOL RULES

### 2.1 Envelope Schema (v0.1 + R0 Patch)

Every message MUST use the following envelope structure:

```
ALVIANTECH_ENVELOPE v0.1

PORTS:
  msg_id: "msg-NNNN"
  ts_utc: "YYYY-MM-DDTHH:MM:SSZ"
  from: {{SENDER}}            # HUMAN | TRINITY | MORPHEUS | {{AGENT_NAME}}
  to: {{RECIPIENT}}           # HUMAN | TRINITY | MORPHEUS | {{AGENT_NAME}}
  mode: {{MODE}}              # DESIGN | EVAL | EXEC | REFLECT
  scope: {{SCOPE}}            # NON_EXEC | EXEC_CONFIRMED | REVIEW_ONLY

BODY:
  goal: {{free text — one sentence stating purpose}}
  inputs:
    - {{bullet list of relevant context}}
  constraints:
    must:
      - {{required conditions}}
    must_not:
      - {{prohibited conditions}}
  output_spec:
    type: {{ARTEFACT | DECISION | QUESTION | LOG}}
    format: {{MARKDOWN | PLAINTEXT | JSON}}
  payload:
    {{main content of the message}}

RETURN:
  in_reply_to: "msg-NNNN"
  exit: {{PASS | FAIL | DEFER | ESCALATE | blank}}
  reason:
    - {{bullet explanation}}
  payload:
    {{response content}}
```

### 2.2 R0 Patch — Integrated

The R0 patch is now frozen into the schema above. The following fields
were added at R0:

| Field          | Added at | Purpose                                   |
|----------------|----------|-------------------------------------------|
| `mode`         | R0       | Classify intent of the message.           |
| `scope`        | R0       | Declare execution authority.              |
| `exit`         | R0       | Structured outcome code on RETURN.        |
| `output_spec`  | R0       | Declare expected output type and format.  |

No further schema mutations are permitted without a new versioned
patch (R1+), which must itself be proposed via an envelope.

### 2.3 Append-Only Rule

- **No message, once committed, may be edited or deleted.**
- If a message contains an error, the correction MUST be issued as a
  new envelope with:
  - `in_reply_to` referencing the erroneous message.
  - A `BODY.goal` beginning with `CORRECTION:`.
- Git enforces this via commit history. Force-pushes to `main` are
  prohibited by policy.

### 2.4 Message ID Sequence

- IDs are sequential: `msg-0001`, `msg-0002`, `msg-0003`, ...
- The HUMAN is responsible for assigning the next ID when authoring.
- An AI agent replying uses the same ID with suffix `-R`:
  e.g., `msg-0001` → reply is `msg-0001-R`.
- A new topic or thread increments the sequence number.

### 2.5 Evaluation Policy (FROZEN)

**Policy: HUMAN-IN-THE-LOOP REVIEW**

All messages with `scope: EXEC_CONFIRMED` require explicit HUMAN
approval before any execution occurs. Evaluation proceeds as follows:

1. Agent produces output with `scope: REVIEW_ONLY` or `scope: NON_EXEC`.
2. HUMAN reviews and either:
   a. Approves → re-issues or annotates with `scope: EXEC_CONFIRMED`.
   b. Rejects → issues a new envelope with `exit: FAIL` and reason.
   c. Defers → issues a new envelope with `exit: DEFER`.
3. No agent may self-approve execution.
4. This evaluation policy is **FROZEN at v0.1** and may only be changed
   via a versioned protocol amendment (proposed via envelope, approved
   by HUMAN).

---

## 3. AGENT REGISTRY

| Agent Name | Role                          | Status   |
|------------|-------------------------------|----------|
| HUMAN      | Owner, final authority        | ACTIVE   |
| TRINITY    | Primary AI governance agent   | ACTIVE   |
| MORPHEUS   | Design/architecture agent     | ACTIVE   |

---

## 4. MESSAGE LOG

> All messages are appended below this line. Never edit above the
> divider except via a versioned protocol amendment.

---

### msg-0001

```
ALVIANTECH_ENVELOPE v0.1

PORTS:
  msg_id: "msg-0001"
  ts_utc: "2026-02-18T09:30:00Z"
  from: HUMAN
  to: TRINITY
  mode: EVAL
  scope: NON_EXEC

BODY:
  goal: Test postbox transport — confirm TRINITY can parse this envelope
        and reply using the correct schema.
  inputs:
    - This is the first message in the alviantech-comms postbox.
    - The postbox has moved from HF Space to Git to preserve raw text
      and enforce append-only logging.
    - TRINITY should confirm receipt and reply with a structurally
      valid envelope.
  constraints:
    must:
      - Reply must use ALVIANTECH_ENVELOPE v0.1 schema exactly.
      - Reply msg_id must be "msg-0001-R".
      - Reply must confirm parsing of all PORTS and BODY fields.
    must_not:
      - No external links or citations.
      - No schema mutations.
  output_spec:
    type: LOG
    format: MARKDOWN
  payload:
    TRINITY — this is a format mismatch test. Parse this envelope and
    reply below using the exact schema. Confirm you can read all fields.
    If any field is ambiguous or unparseable, flag it in your RETURN
    payload.

RETURN:
  in_reply_to: ""
  exit:
  reason:
    -
  payload:

```

---

*End of msg-0001. Next message appended below.*

---
