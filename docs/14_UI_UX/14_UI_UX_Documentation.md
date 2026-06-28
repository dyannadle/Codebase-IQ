# UI/UX Documentation

**Project Name:** CodebaseIQ - AI-Powered Repository Intelligence Platform  
**Document Number:** UX-001  
**Version:** 1.0.0  
**Date:** June 2026  
**Confidentiality:** Internal / Restricted  

---

## Document Control

### Version History
| Version | Date | Author | Description of Changes |
| :--- | :--- | :--- | :--- |
| 0.9.0 | 2026-06-25 | UI/UX Lead | Initial Design System Draft |
| 1.0.0 | 2026-06-28 | Product Team | Final Approval |

### Table of Contents
1.  Design System Overview
2.  Color Palette & Typography
3.  Component Library & Layouts
4.  Accessibility (a11y)
5.  Micro-interactions & Animation

---

## 1. Design System Overview
CodebaseIQ utilizes a customized version of **Shadcn UI** combined with **Tailwind CSS**. The aesthetic is "Premium Developer Tool" — utilizing dark modes, subtle glassmorphism (translucency), high-contrast borders, and technical, monospaced typography for code blocks. 

*   **Primary Theme:** Dark Mode is the default and primary theme, as it is the overwhelming preference for software developers. A Light Mode is provided for accessibility compliance.
*   **Grid System:** 12-column responsive grid based on Tailwind's default breakpoints (`sm`, `md`, `lg`, `xl`, `2xl`).

## 2. Color Palette & Typography

### 2.1 Color Palette (Dark Mode Default)
*   **Background:** `#09090B` (Zinc-950) - Deep, almost-black background.
*   **Surface / Cards:** `#18181B` (Zinc-900) - Slightly lighter for floating elements.
*   **Primary Accent:** `#3B82F6` (Blue-500) - Used for primary call-to-action buttons (e.g., "Connect GitHub").
*   **Success:** `#10B981` (Emerald-500) - Used for "Sync Complete" badges.
*   **Error:** `#EF4444` (Red-500) - Used for failed syncs and destructive actions (e.g., "Delete Repository").
*   **Text (Primary):** `#FAFAFA` (Zinc-50) - High contrast text.
*   **Text (Muted):** `#A1A1AA` (Zinc-400) - Secondary information and placeholders.

### 2.2 Typography
*   **Primary Font (UI):** `Inter` (sans-serif) - Highly legible, modern, and clean for dashboards and navigation.
*   **Monospace Font (Code):** `JetBrains Mono` or `Fira Code` - Used exclusively for rendering source code, citations, and terminal output. Supports programming ligatures.
*   **Base Size:** 16px.
*   **Scale:** Minor Third (1.200).

## 3. Component Library & Layouts

### 3.1 Core Components
*   **Sidebar (Left):** Collapsible navigation. Contains links to Chat, Repositories, Analytics, and Settings.
*   **Chat Interface (Center):** The primary view. Features a sticky input box at the bottom, message history bubbling up, and Markdown rendering support.
*   **Split Pane (Right - Collapsible):** When a user clicks an inline citation, this pane slides in from the right to display the raw source code via the Monaco Editor.

### 3.2 Design Tokens
Design tokens are managed in `tailwind.config.js`. Avoid hardcoding hex values in React components. Always use the semantic classes (e.g., `text-primary`, `bg-background`).

## 4. Accessibility (a11y)
The platform aims for **WCAG 2.1 AA** compliance.

*   **Keyboard Navigation:** All interactive elements must have visible `:focus-visible` rings (using Tailwind's `ring-2 ring-primary`).
*   **Contrast:** The text-to-background contrast ratio must be at least 4.5:1.
*   **Screen Readers:** Use semantic HTML (`<nav>`, `<main>`, `<aside>`) and ARIA labels (`aria-label`, `aria-describedby`) on icon-only buttons (e.g., the "Send Message" arrow icon).
*   **Reduced Motion:** Respect the user's OS-level `prefers-reduced-motion` setting by disabling CSS transition animations when active.

## 5. Micro-interactions & Animation

*   **LLM Streaming:** As text streams in from the AI, the chat bubble should smoothly expand. Avoid harsh jumping of the scrollbar.
*   **Hover States:** Buttons and interactive cards should slightly elevate (`-translate-y-1`) or brighten upon hover to provide tactile feedback.
*   **Loading States:** Instead of static spinners, use animated Skeleton loaders (Shadcn `Skeleton` component) that match the shape of the content being loaded (e.g., skeleton text lines for chat, skeleton boxes for repo cards).
*   **Toast Notifications:** Slide in from the bottom-right using a spring physics animation (`framer-motion`), pausing on hover, and dismissing after 5 seconds.
