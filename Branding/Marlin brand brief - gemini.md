{\rtf1\ansi\ansicpg1252\cocoartf2639
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;\f1\fnil\fcharset0 AppleColorEmoji;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 # 
\f1 \uc0\u55356 \u57263 
\f0  BRANDING & DESIGN BRIEF: MARLIN GRADE (MVP)\
\
You are an expert UI/UX designer and brand strategist. Your goal is to design the visual identity, design token framework, and MVP core dashboard interface layouts for **Marlin Grade** (marketed consumer-facing as **Marlin**). \
\
Read the comprehensive strategic layout below to execute cohesive assets that match this specific brand archetype.\
\
---\
\
## 
\f1 \uc0\u55357 \u56960 
\f0  1. Executive Summary & Brand Positioning\
*   **The Product:** A B2B real estate predictive analytics SaaS platform for solo agents and small teams.\
*   **The Value Proposition:** It aggregates scattered, disorganized public county records (Appraisal Districts, Probate Courts, Code Enforcement, Permits) into a unified dashboard. It scores individual residential addresses with a predictive letter grade (**A+ to F**) indicating their exact likelihood to go on the market within the next 12 months.\
*   **The Market Context:** Based initially out of **Austin, TX**, expanding city-by-city across Texas.\
*   **The Anti-Persona:** We are **NOT** a consumer home-search app (like Zillow or Trulia), nor a friendly, warm brokerage site. We are **NOT** a fishing charter or seafood restaurant. Avoid houses, roofs, location pins, and literal fish icons.\
*   **The Persona:** High-end, precise, predictive data-intelligence. Think *Palantir*, *Scale AI*, or *Bloomberg* tailored specifically for elite real estate listing agents. It feels fast, exclusive, high-density, and highly authoritative.\
\
---\
\
## 
\f1 \uc0\u55356 \u57256 
\f0  2. Visual Identity & Design Tokens\
\
### Logo & Wordmark Concept\
*   **The Logo Mark:** An abstract, geometric "Sword & Signal" glyph. A stylized, upward-slanting chevron or lightning bolt that evokes the fast bill and sharp dorsal fin of a marlin. The body of the glyph should be sliced vertically to mimic a progressive bar chart or data stream.\
*   **The Wordmark:** Formatted in all-caps, modern, geometric sans-serif font. The letter **"A"** in **MARLIN** has its horizontal crossbar removed, turning it into a clean, upward-pointing chevron (`^`). \
*   **Full App Hierarchy:** "MARLIN" is rendered in a heavy black weight; "GRADE" is right-aligned directly underneath in a lighter font-weight with wide tracking.\
\
### Color Palette ("Deep Analytics")\
*   **Abyssal Blue (`#0B111E`):** The primary workspace background. The default state of the app is **Dark Mode** to convey data sophistication.\
*   **Marlin Ice (`#F1F5F9`):** Primary typography, crisp container borders, and structural dividing lines. Maximum legibility on dark surfaces.\
*   **Signal Cyan (`#00F0FF`):** The primary accent and action color. Used for interactive buttons, pulsing target states, and "A-Grade" predictive property highlights.\
*   **Data Green (`#00E676`):** The operational payoff color. Used exclusively for "Export to CSV" buttons, revenue growth metrics, and volume trackers.\
*   **Subdued Slate (`#64748B`):** Secondary body text, low-propensity "F-Grade" labels, and background grid lines.\
\
### Typography Stack\
*   **Headers & Branding:** *Plus Jakarta Sans* or *Cabinet Grotesk* (Bold to Black weights, tight letter-spacing for punchy, technical headings).\
*   **Interface & Data:** *Inter* or *SF Pro Display* (Highly readable sans-serif optimized for heavy tabular grids and address listings).\
*   **Data Labels (Optional Accent):** *JetBrains Mono* (Used sparingly for parcel IDs, tax values, or system timestamp logs to emphasize raw data calculation).\
\
---\
\
## 
\f1 \uc0\u55357 \u56741 \u65039 
\f0  3. MVP Interface Architectures & Cues\
\
### Layout Archetype: High-Density Workspace\
The user interface bypasses heavy graphic padding in favor of a clean, structured **three-section layout** designed for rapid decision-making:\
1.  **Sticky Global Header:** Features a centered, prominent lookup bar with an active **Signal Cyan** glowing border state, allowing ad-hoc address queries.\
2.  **Left Sidebar Navigation:** Minimalist icon states (`Dashboard`, `Tracked Zips`, `Export Logs`, `Settings`).\
3.  **Core Data Workspace:** A tabular grid display packed with property rows that can be sorted by Zip Code or Marlin Grade. High-probability properties (A and B grades) flash a crisp, glowing Signal Cyan pill tag. Lower grades melt passively into the Abyssal Blue background layout to optimize the agent\'92s visual focus.\
\
### The "Marlin Grade" Widget\
Rather than plain flat text, the predictive score is a standalone UI element:\
*   A circular data gauge with a percentage ring that lights up in **Signal Cyan**.\
*   The large letter grade (e.g., **A+**) sits dead center, flanked underneath by micro-monospaced technical metadata flags detailing why the score spiked (e.g., `TENURE: 14 YRS` | `HOMESTEAD: DROPPED`).\
\
---\
\
## 
\f1 \uc0\u55357 \u56541 
\f0  4. Prompt Instructions for Next Steps\
Using this design brief, please generate the following design deliverables:\
*   An **SVG implementation or detailed CSS rendering layout** for the abstract, geometric Marlin icon and altered custom wordmark.\
*   The interactive UI layout code or a clean layout framework for the **MVP Dashboard Page**, showing the sticky search bar, the high-density farm workspace data table, and the Data Green bulk CSV export elements.\
*   A component design pattern for the right-hand **Address Deep-Dive Slide-Out Drawer**, displaying the positive and negative property data triggers.\
}