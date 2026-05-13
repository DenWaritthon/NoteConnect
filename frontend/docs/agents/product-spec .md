# NoteConnect Product Specification

## Product Overview

NoteConnect is a smart note-taking web application that automatically analyzes relationships between notes and visualizes them as an interactive graph.

The experience combines:
- Apple Notes style note-taking
- Knowledge graph visualization
- AI-generated relationship analysis

The frontend should feel:
- lightweight
- intelligent
- modern
- interactive
- productivity-focused

---

# Main Pages

1. Landing Page
2. Workspace Page
3. Graph Page
4. Relation Detail Page
5. Settings Page

---

## Landing Page

Purpose:
Introduce NoteConnect and guide users into the application.

Sections:
- navigation bar
- hero section
- feature highlights
- footer

Main CTA:
- Open Workspace
- Try NoteConnect

---

## Workspace Page

Purpose:
Main workspace for note management and relationship exploration.

Main Areas:
- folder sidebar
- notes workspace
- graph access button
- relation interactions

---

# Core Features

## Folder Management

Users can:
- create folders
- edit folders
- delete folders
- switch between folders

## Note Management

Users can:
- create notes
- edit notes
- delete notes
- auto-save notes
- navigate between notes

## Relationship Visualization

The system should:
- visualize relationships between notes
- support graph interaction
- support zoom/pan/drag
- display relation metadata
- display similarity scores

## AI Explanation

Users should be able to:
- generate relation explanations
- read generated explanations
- view explanation panels or modals

---

# Responsive Design

The application must support:
- desktop
- tablet
- mobile

Mobile expectations:
- collapsible sidebar
- fullscreen graph modal
- touch-friendly controls
- responsive navigation

---

# Suggested Frontend Stack

Core:
- Next.js
- React
- TypeScript

Styling:
- Tailwind CSS

State:
- Zustand

Graph:
- React Flow

Animation:
- Framer Motion

---

# UI/UX Design Direction

Style:
- Minimal
- Modern
- Productivity-focused workspace
- Apple Notes inspired

Theme Requirements:
- The primary application color theme should be based on the colors used in the logo file:
  - `note-connect/public/note-connect.svg`
- The frontend project is located in:

```text
note-connect/
```
- The UI color palette should stay visually consistent with the branding and logo identity.
- Avoid introducing unrelated dominant colors that conflict with the logo theme.
- Prefer a clean monochromatic or logo-aligned accent palette.

Theme Modes:
- Support both Light Mode and Dark Mode.
- Theme switching should affect:
  - background colors
  - text colors
  - borders
  - cards/panels
  - graph visualization colors
  - buttons and interactive states
- Dark mode should preserve readability and accessibility.
- Theme transitions should feel smooth and modern.

---

# Suggested Future Features

Optional future improvements:
- Markdown support
- Rich text editor
- AI note summarization
- Tag system
- Search functionality
- Real-time collaboration
- Authentication system

---

# UX Expectations

The experience should prioritize:
- fast note-taking
- smooth transitions
- instant feedback
- keyboard accessibility
- responsive layouts
- minimal distractions
- lightweight interactions

---

# Overall Goal

The NoteConnect frontend should combine:
- fast note-taking
- visual thinking
- relationship discovery
- knowledge organization

The UI should feel:
- clean
- modern
- responsive
- intelligent
- focused
