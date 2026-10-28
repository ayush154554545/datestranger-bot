# ADR 007: Next.js + TypeScript for Web & SEO Landing Pages

## Context
The website component requires search engine optimization (SEO), fast initial page loads, dynamic metadata, structured schema markup, and responsive design.

## Decision
Build `website/` using **Next.js (App Router)** with **TypeScript**.

## Alternatives Considered
- Static HTML (Legacy `index.html`): Lacks SSR, blog features, dynamic open graph metadata, and modular React components.
- Single Page Application (React SPA): Poor SEO indexability for marketing landing pages.

## Consequences
- Full Server-Side Rendering (SSR) and Static Site Generation (SSG).
- Superior Core Web Vitals, Open Graph metadata, sitemap.xml, and schema markup.

## Status
ACCEPTED
