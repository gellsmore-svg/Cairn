## 1. Role-play snapshots

### novice-repair-user

**Observed evidence:** The user must find `.composer__input`, enter an underspecified request, receive an answer, then repair the request with more context.

**Awareness:** They may only realise the request was incomplete after the first assistant answer fails to resolve it. The interface appears to rely on the user noticing missing object, authority, and source context.

**Execution:** They must remember what they meant, identify what was missing, phrase the repair clearly, and decide how much uncertainty to disclose.

**Notification/closure:** Closure is weak: the user must judge whether the second answer is now good enough. There is no observed explicit “missing context resolved” or “evidence sufficient” signal.

**Recovery:** Recovery depends on the user reconstructing details and resisting premature acceptance. A novice may treat the repair as complete because the system responded, not because the answer is grounded.

**Organisational pressure:** Inference: if this is used in operational work, the novice may over-trust the assistant to avoid looking slow or asking for help.

### queue-pressure-operator

**Observed evidence:** The flow used 1 click, 2 fills, 2 waits, and 1 context switch into process trace.

**Awareness:** They must notice both the business task and the quality problem in the assistant response while moving quickly.

**Execution:** They must add context under time pressure, compare first and second answers, and possibly inspect process trace to confirm state changed.

**Notification/closure:** The interface does not appear to provide a strong closure marker. The operator may close the loop once two assistant bubbles exist rather than after checking authority or evidence.

**Recovery:** Delays or missing details can create repeat repair turns. The process trace adds audit value but also requires attention switching.

**Organisational pressure:** Inference: queue incentives may reward throughput over careful uncertainty management, especially if audit checks are separate from the main work surface.

### accountable-approver-without-authority-evidence

**Observed evidence:** The scenario explicitly involves accountability, authority gaps, trust calibration, audit reasoning, and uncertainty management.

**Awareness:** They must detect that the assistant’s answer may not carry sufficient authority or source evidence.

**Execution:** They must decide whether they are allowed to approve, whether the answer cites enough source context, and whether the repair turn actually changed the process state.

**Notification/closure:** Closure is socially and procedurally risky: the approver may be accountable for a decision without seeing clear evidence that the system has incorporated the correction.

**Recovery:** If information is missing or wrong, they may need to escalate, reopen the request, inspect trace, or document uncertainty manually.

**Organisational pressure:** Inference: this role is exposed to blame asymmetry: they may be expected to approve quickly but lack the authority evidence needed to defend the approval later.

## 2. Likely load amplifiers

- **Observed:** The user must move from composition to process inspection, creating at least one context switch.
- **Observed:** The repair turn requires recall, language formulation, uncertainty management, and accountability judgment.
- **Observed:** Closure clarity is marked as uncertain.
- **Inference:** The deterministic adapter/configuration control may add system-use overhead for ordinary users if exposed outside testing.
- **Inference:** The assistant response may create false closure because “an answer arrived” can feel like completion even when authority or evidence remains unresolved.

## 3. Failure or recursion loops

- User submits unclear request → assistant answers partially → user repairs → assistant answers again → user must still infer whether the repair was incorporated.
- User lacks source context → asks assistant anyway → assistant produces plausible answer → user becomes accountable for unsupported output.
- Operator opens process trace → sees process state but not decision sufficiency → returns to conversation → repeats clarification.
- Approver sees missing authority → asks for evidence → receives more text but still no explicit provenance or approval boundary.

## 4. Suggested Cairn annotations

```text
HUMAN_DEMAND:
AWARENESS: User must identify the input surface and later recognise that the assistant response has not resolved missing context.
EXECUTION: User must supply object, authority, source context, and uncertainty details during repair.
NOTIFICATION: Closure depends on human judgment rather than explicit system confirmation.
RECOVERY: Repair may require recall, escalation, and audit inspection.
ORGANISATIONAL_PRESSURE: Throughput and accountability may conflict when evidence is incomplete.
```

```text
HUMAN_FACTORS:
uncertainty_load: User must decide whether missing context has been resolved.
authority_gap: User may be asked to act without clear source or approval evidence.
recovery_recursion: Repair turns can create repeated checking work.
attention_switching: Process trace inspection moves the user into audit mode.
trust_calibration: Assistant response presence may be mistaken for sufficient completion.
```

```text
HUMAN_RISK:
probability: medium
impact: high
confidence: medium
rationale: Based on observed repair loop, uncertain closure, accountability demands, and explicit process-trace inspection.
```

## 5. Questions for the developer or process owner

1. What visible signal tells the user that missing object, authority, and source context have been resolved?
2. Can the assistant mark unresolved authority gaps before giving an actionable answer?
3. Is the process trace meant for ordinary operators, approvers, auditors, or testers?
4. What evidence must be present before a user is allowed to close or approve the work?
5. Are repair turns logged as changes in process state, or only as conversation history?
6. Under queue pressure, what prevents users from accepting the second answer without checking provenance?