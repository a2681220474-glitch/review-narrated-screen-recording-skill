---
name: review-narrated-screen-recording
description: Review narrated screen recordings by extracting audio, transcribing speech, sampling frames, aligning spoken feedback with the visible product state, optionally checking the current code, and producing a timestamped confirmation checklist before implementation. Use for screen-recording acceptance reviews, QA videos, UX walkthroughs, bug-report videos, or requests such as "我边录屏边说问题", "把视频里的问题列出来", "对齐画面和声音", and "先核对再修改".
---

# Review Narrated Screen Recording

Turn a screen recording with spoken commentary into a reliable, evidence-linked acceptance checklist. Treat the speaker's words as the source of requested changes and the video as the source of page and interaction context.

## Operating Contract

- Default to analysis only. Do not edit product files until the user confirms the checklist or explicitly asks for immediate implementation.
- Use the supplied recording from the current request as evidence. Do not substitute old screenshots or prior audit conclusions.
- Preserve timestamps throughout extraction, transcription, inspection, and reporting.
- Distinguish requested changes from observations, questions, approvals, retractions, and narration.
- Let later speech override earlier speech. For example, "这个搜索添加是……哦，没事" means no change.
- State uncertainty instead of guessing when speech or visuals are ambiguous.

## Workflow

### 1. Establish The Baseline

Identify:

- source video path
- product or repository, when available
- requested review scope
- output directory
- whether the user wants review only or implementation after confirmation

Use a local temporary output directory by default, such as `/private/tmp/narrated-review-<video-stem>`. If a repository is involved, record `git status --short` and the current commit before analysis. Do not clean or revert unrelated work.

### 2. Prepare Evidence

Check for `ffmpeg`, `ffprobe`, and a transcription provider. Prefer local `whisper-cli` with a multilingual model for private recordings.

Run:

```bash
python3 scripts/prepare_review.py /absolute/path/video.mov \
  --output /private/tmp/narrated-review-video \
  --interval 1 \
  --language zh \
  --model /absolute/path/ggml-small.bin \
  --prompt "产品名、页面名和功能名"
```

The script creates:

- `metadata.json`
- `audio-16k.wav`
- `frames/frame_*.jpg`
- `sheets/sheet_*.jpg`
- `frame-manifest.json`
- `transcript.txt`, `transcript.srt`, and `transcript.json` when Whisper succeeds
- `timeline.json` mapping transcript segments to nearby frames

If a model is unavailable, run the script without `--model`, then use an available speech-to-text service and save SRT in the same output directory. Never pretend that silent visual inspection includes the spoken feedback.

### 3. Read The Entire Transcript

Read the transcript from start to finish before creating findings. For each segment, classify the speaker's intent as one of:

- `change`: asks to add, remove, move, rename, restyle, or restrict something
- `problem`: reports broken, confusing, or incorrect behavior
- `approval`: explicitly says the current behavior is fine
- `retraction`: withdraws or corrects an earlier concern
- `question`: asks why something exists or behaves this way
- `narration`: describes navigation without requesting a change
- `ambiguous`: cannot be safely interpreted

Correct obvious ASR mistakes only when the visual and surrounding speech make the intended term clear. Record the correction in the evidence notes. Keep uncertain wording marked as uncertain.

### 4. Inspect The Video Chronologically

Inspect every contact sheet in order. Around each spoken change, problem, question, approval, or retraction:

1. Open the nearest full-resolution frame.
2. Inspect at least two seconds before and after when interaction context matters.
3. Record the visible page, scroll position, control, action, loading state, and result.
4. Reject frames that are blank, mid-transition, obscured, or unrelated.
5. Capture a better exact frame when the sampled frame is insufficient.

Do not infer a requested change from a visual difference alone. Place unspoken visual issues in a separate optional section labeled `Visible but not spoken`.

### 5. Cross-Check The Current Product

When source code is available, locate the visible text, handler, route, state, and permission check. Mark each spoken point as:

- `missing`
- `present but wrong`
- `partially complete`
- `already satisfied`
- `not verifiable from code read`

For permission-sensitive features, check both entry visibility and server-side authorization. A hidden button without backend enforcement is incomplete; a protected endpoint with a publicly claimable admin role may also be incomplete.

Do not edit files during this step.

### 6. Consolidate Spoken Points

Create one checklist item per independent user intent. Merge repeated comments about the same behavior. Preserve separate items when the desired actions differ.

Each item must contain:

- timestamp range
- page or flow
- concise spoken intent
- visible evidence
- current implementation state, when code was checked
- proposed action
- confidence: high, medium, or low
- status: `需改`, `部分完成`, `已满足`, `不改`, or `待确认`

Apply these rules:

- A later correction overrides an earlier statement.
- "没事", "这个不用了", and equivalent language become `不改` unless later reversed.
- Questions such as "为什么放这里" usually imply a concern, but keep the proposed destination as `待确认` unless the speaker states it.
- Do not transform one narrow request into a broad redesign.
- Keep explicitly deferred items visible as `暂不处理` so they are not changed accidentally.

Use [references/checklist-format.md](references/checklist-format.md) for the final structure.

### 7. Ask For Confirmation

Return the checklist before implementation. Lead with the baseline state and clearly say that no product files were modified.

Include:

- confirmed change items
- partial or already-complete items
- explicit no-change items
- ambiguous items requiring confirmation
- transcript and evidence folder paths
- evidence limitations

Do not ask the user to repeat feedback already recoverable from the recording.

### 8. Implement Only After Confirmation

When the user confirms, treat the confirmed checklist as the implementation contract. Preserve deferred and no-change items. After implementation, verify each confirmed item against the original timestamped evidence and report any remaining mismatch.

## Quality Gates

Before handing off the checklist, verify:

- The full audio was transcribed or a named blocker was reported.
- Every transcript segment with actionable intent was accounted for.
- Every change item has visual evidence from the matching time range.
- Approvals and retractions were not accidentally converted into tasks.
- Repeated comments were deduplicated without losing distinct actions.
- Code status was checked only when code was available.
- No product files were changed during review-only mode.
- The user can approve items by number without rereading the whole transcript.
