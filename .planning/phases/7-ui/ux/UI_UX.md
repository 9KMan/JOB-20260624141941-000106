# UI/UX Approach — AI Report Writer

## Pages / Flow

The app follows a 4-step linear workflow, configured by `config/app.json`:

| Page | Purpose |
|------|---------|
| 1. Upload | User uploads one or more PDF documents |
| 2. Decisions | User enters key decisions (interview type, focus areas) |
| 3. Review | LLM-generated narrative is displayed; user edits |
| 4. Export | User clicks Export → Word document is saved |

## Layout

Single-window Qt app with a `QStackedWidget` showing one page at a time. Each page has:
- Top bar: app title + step indicator (1/4, 2/4, ...)
- Center: page-specific widget
- Bottom: navigation buttons (Back, Next, Cancel)

## Component Inventory

- **UploadWidget**: drag-and-drop area, file list, "Remove" button
- **DecisionsWidget**: form with text inputs + checkboxes
- **ReviewWidget**: large `QPlainTextEdit` for narrative; save-on-blur
- **ExportWidget**: template selector, output path picker, progress bar

## UX Patterns

- **Config-driven**: All page labels, button text, default values come from `config/app.json` — no hardcoded UI strings
- **Plain-text prompts**: All LLM prompts loaded from `config/prompts/*.txt` — non-developers can edit
- **Async LLM calls**: Bedrock calls run in a `QThread` to keep UI responsive
- **Cancel anytime**: User can back out of any step without losing uploads

## Accessibility

- Keyboard navigation: Tab order follows visual flow
- Screen reader labels via `setAccessibleName()` on all interactive widgets
- Minimum window size: 1024x768
