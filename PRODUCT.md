# Product

## Register

brand

## Users

Design-conscious iOS users. They notice typography, icons, micro-interactions, and craft on first scroll. They follow design Twitter / Mastodon, check Mac App Store editorial picks, read Daring Fireball / Sidebar / It's Nice That. They will happily pay $5–10 once for a calculator that's clearly been made by someone who cares — and they're equally happy to close the tab in 4 seconds if it smells like a template.

Visiting context: usually desktop or tablet first (researching, sharing with friends), then iPhone to actually tap "Get" on the App Store. Browser sessions are short; the site has to earn the next scroll, not assume it.

## Product Purpose

Calco / 01 is a premium iPhone & iPad calculator app by Matteo Vitali, published by Clickstudio Digital Marketing Co LLC (Dubai, UAE): skeuomorphic, tactile, with the precision of a modern OS and the warmth of a 1980s Casio MS-80. Seven modes (Basic, Scientific, Currency, Units, TVM, Date, %). One-time purchase. No ads, no subscriptions, no tracking.

The marketing site has **one job**: convert design-conscious visitors into App Store downloads. Every section ladders up to that. Secondary outcome: signal Matteo's taste so the site itself is share-worthy on design circles (which feeds the funnel).

Success looks like: a visitor scrolls, smiles at a detail, taps the App Store CTA. Not "spends 3 minutes reading features," not "signs up for a newsletter." Tap and go.

## Brand Personality

**Skeuomorphic. Nostalgic. Premium.**

The voice belongs to someone who has thought hard about why old calculators felt better than new ones, and decided the answer matters. It references the Casio MS-80 without being precious about it. It says "math feel premium" with a straight face because it means it.

It does NOT use exclamation points, "amazing," "powerful," or "best ever." It does NOT write feature bullets that sound like an Asana onboarding flow. It does NOT call itself "delightful" — it just is. Calm declarative sentences. Occasional dry observation ("My calculator shouldn't have a personality. This one does, and I forgive it."). Heritage references are earned through real proof (the Casio side-by-side photograph), never invoked as decoration.

## Anti-references

**Generic SaaS landing pages.** No three-column feature grids with identical icon + heading + paragraph cards. No hero-metric template (big number, small label, gradient accent). No "Trusted by" logo wall. No "Get started for free" two-CTA dance. If a section pattern would feel at home on a Linear/Stripe/Notion clone, it doesn't belong here.

**Indie-dev casual / playful.** No hand-drawn icons, no comic-cousin display fonts, no `❤️` in the footer, no emoji-heavy headlines, no "I made this in a weekend" voice. The product asks money for craft; the site has to look like craft, not a hobby.

**AI-slop signals.** Gradient-clipped text headlines. Glassmorphism applied to everything. Bauhaus knockoffs that are just primary colors on a grid. Stock photo of a person at a coffee shop generically holding a phone. If a thoughtful designer would say "an LLM made that," rework it.

**App Store screenshot dump.** Five iPhone mockups in a horizontal scroll, each next to a feature bullet. Lazy and unsellable for this price point.

## Design Principles

**1. Heritage as headline, not decoration.** The Casio MS-80 reference, the 1980s desk-calculator lineage, the brushed-aluminum panel — these aren't visual seasoning. They're the actual reason the product exists, and the site should treat them that way. Lean into nostalgia hard enough that it can't be confused with retro pastiche.

**2. Real over rendered.** Whenever showing the product, prefer real-feeling lifestyle photography (hands on an iPad in a daylight room, an iPhone on a walnut desk at dusk, the Casio + iPhone editorial flat-lay) over floating product mockups or feature-card icon grids. Real beats clever; texture beats template.

**3. Show the app; don't market the app.** Every major section puts the actual app, its colors, or its tactile detail on screen at scale. The copy should never explain craft that the image already proves. If you can delete a sentence and the section still says the same thing, delete the sentence.

**4. Quiet confidence. No shouting.** Trust the visitor to notice. No superlatives, no urgency, no "limited time," no exclamation points. Calm typography, generous whitespace, occasional dry wit. The site behaves like someone who knows the calculator is worth the money and doesn't need to convince anyone twice.

**5. Match the price-point in pixels.** This calculator costs more than the stock iOS one for a reason; the marketing site has to look as premium as the ask. Photography quality, typographic restraint, spacing rhythm, motion easing, and copy density all need to read as "considered" within 2 seconds. If anything on the page looks cheap, the app feels overpriced.

## Accessibility & Inclusion

**WCAG 2.1 AA baseline.** This is a consumer marketing site for a premium product; meeting the standard professional bar is non-negotiable and unremarkable, not aspirational.

Specifically:

- Text contrast meets AA at body and large-text sizes across both Warm and Neon themes.
- All interactive elements (theme toggle, CTAs, day/night toggle, testimonial cards on hover) have visible focus indicators.
- `prefers-reduced-motion: reduce` honored: hero parallax tilt freezes, IntersectionObserver reveal animations skip the entrance transform, the day/night phone crossfade collapses to an instant swap. Already implemented in v2/v3.
- Every image has descriptive alt text — not generic "calculator" but "iPhone showing Calco Warm theme on an oak desk with a leather notebook and espresso."
- Semantic HTML: real `<button>` for the toggle (already done), real `<section>` landmarks, headings in document order, `aria-label` on icon-only controls, `role="radio"` with `aria-checked` on the day/night toggle group.
- Theme/palette color is never the only signal for state. Active states also use ring outlines, weight changes, or label changes, not color alone — so color-blind visitors see the same selection feedback.
- The site degrades gracefully on iPhone touch and supports the native iOS theme via `prefers-color-scheme`.
