# Confirmation Checklist Format

Use this compact structure. Keep the main checklist readable; place deeper audit notes in the evidence directory.

```markdown
Source: <recording path>. Evidence preparation: complete or named blocker.

## 待确认清单

1. **<page and issue> | 需改**
   - Time: 00:12-00:24
   - Surface/input: mobile / inferred tap
   - Spoken intent: <clean paraphrase>
   - Visible evidence: <what the matching frames show>
   - Visible state: <what the recording shows before and after the interaction>
   - Proposed action: <bounded change>
   - Confidence: high

2. **<page and behavior> | 不改**
   - Time: 00:40-00:49
   - Reason: Speaker reviewed it and then said it was fine.

## 待确认歧义

- <exact ambiguity and the narrow decision needed>

Evidence: <transcript path> | <timeline path> | <screenshots folder>
```

## Health Labels

- `需改`: clear requested change that is not visibly satisfied in the recording
- `部分完成`: capability exists but does not fully satisfy the spoken requirement
- `已满足`: the visible state already matches the spoken requirement
- `不改`: speaker explicitly approved, withdrew, or deferred the point
- `待确认`: the desired action or destination cannot be derived safely

## Evidence Notes

For each actionable point, preserve a machine-readable or Markdown note containing:

- `start`
- `end`
- `surface`
- `input_method`
- `interaction_indicator`
- `transcript_raw`
- `transcript_clean`
- `intent_type`
- `page`
- `frame_paths`
- `status`
- `confidence`
- `reasoning_limit`
