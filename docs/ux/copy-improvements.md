# DateWithStranger - Copy Refactor & UX Improvements

## Overview
This document records the before/after copy refactoring across the DateWithStranger application. The goal of this refactor is to eliminate verbose, slow-to-read, overly technical, and unengaging copy in favor of short, clear, friendly, action-oriented product copy with visual anchor emojis.

---

## Core Copywriting Principles
1. **Shortest Wording That Remains Completely Clear**: Trim unnecessary fluff while preserving full clarity.
2. **Visual Anchors**: Use meaningful semantic emojis (`🔎`, `🛑`, `⏭️`, `👤`, `⚙️`, `🌍`, `🚨`, `🚫`, `💬`, `⭐`, `🎁`, `✅`, `⚠️`, `❌`, `⏳`) to aid quick scanning on mobile devices.
3. **Action-Oriented Prompts**: Frame buttons and prompts around user actions (`🔎 Find`, `🛑 Stop`, `⏭️ Next`).
4. **Friendly & Conversational**: Avoid mechanical tech jargon (`We were unable to process your request at this time`).
5. **Clean Error Boundaries**: Never expose stack traces, database logs, or API errors to end users.

---

## Before & After Copy Audit Table

| Category | Key | Original Wording | New Improved Wording | UX Justification |
|---|---|---|---|---|
| **Language Selection** | `lang.title` | *None (hardcoded English startup)* | `🌍 Choose your language` | Gives international users immediate language choice before any onboarding text. |
| **Onboarding** | `welcome.title` | `💘 Welcome to Date Stranger! Let's set up your profile — it takes about 30 seconds.` | `👋 Welcome!` | Trims fluff. Simple welcoming header. |
| **Onboarding** | `welcome.subtitle` | `Your details stay anonymous in chats. They are only used to find better matches for you.` | `⚡ Profile setup (30s)` | Direct, scannable subtext explaining quick setup time. |
| **Onboarding** | `onboarding.step1` | `Step 1 of 6: What should we call you? (Pick a nickname, 2–20 letters)` | `👤 Your name?` | Instant question, easy to scan. |
| **Onboarding** | `onboarding.step2` | `Step 2 of 6: How old are you? (Enter a number 13–80)` | `🎂 Your age?` | Direct question; concise age boundary hint. |
| **Onboarding** | `onboarding.step3` | `Step 3 of 6: What's your gender?` | `👤 Choose your gender` | Clear action prompt with inline buttons. |
| **Onboarding** | `onboarding.step4` | `Step 4 of 6: Where are you from?` | `🌍 Where are you from?` | Emoji anchor with country selection. |
| **Onboarding** | `onboarding.step5` | `Step 5 of 6: What language do you speak?` | `🗣 Primary language?` | Short and clear. |
| **Onboarding** | `onboarding.complete` | `🎉 All set, {name}! Your profile is ready ✅` | `🎉 All set, {name}!\nYour profile is ready ✅` | Energetic completion confirmation. |
| **Buttons** | `btn.find` | `🔍 Search Partner` | `🔎 Find` | Single-word action label fitting comfortably on mobile screens. |
| **Buttons** | `btn.next` | `⏭ Next` | `⏭️ Next` | Universal skip emoji with standard text label. |
| **Buttons** | `btn.stop` | `🛑 Stop` | `🛑 Stop` | Clear stop signal button. |
| **Buttons** | `btn.profile` | `📊 View Profile` | `👤 Profile` | Standard profile icon and label. |
| **Buttons** | `btn.settings` | `⚙️ Settings` | `⚙️ Settings` | Standard settings label. |
| **Buttons** | `btn.language` | `🌍 Language` | `🌍 Language` | Language switcher entry point in Settings. |
| **Buttons** | `btn.report` | `🚨 Report` | `🚨 Report` | Immediate reporting action during chat. |
| **Buttons** | `btn.block` | `🚫 Block` | `🚫 Block` | Block button visual anchor. |
| **Matching** | `matching.searching` | `Please wait while we attempt to find another available user for you to communicate with` | `🔎 Finding someone...` | Replaces long tedious text with an active searching state. |
| **Matching** | `matching.connected` | `You have successfully been connected with a partner. You may now begin messaging.` | `💬 You're connected!\nSay hi 👋` | Friendly connection prompt encouraging immediate engagement. |
| **Matching** | `matching.ended` | `Your conversation has successfully ended. You can now search for another person if you would like to continue` | `🛑 Chat ended.` | Short, unambiguous status message. |
| **Matching** | `matching.looking_next` | `Attempting to connect you with another user...` | `⏭️ Finding next partner...` | Dynamic progress message. |
| **Safety** | `report.title` | `User Reporting Interface` | `🚨 Report User` | Friendly header. |
| **Safety** | `report.why` | `Please select a reason for why you are submitting a report against this user` | `Why are you reporting?` | Direct, simple question. |
| **Safety** | `report.sent` | `Your report has been successfully recorded into our moderation system.` | `✅ Report sent. Thanks!` | Concise gratitude confirmation. |
| **Safety** | `block.title` | `Would you like to proceed with blocking this user?` | `🚫 Block this user?` | Simple confirmation question. |
| **Safety** | `block.done` | `The requested user account has been added to your personal block list.` | `🚫 User blocked.` | Instant confirmation. |
| **Errors** | `error.generic` | `We were unable to process your request at this time. Internal error code 500.` | `⚠️ Something went wrong. Try again.` | User-friendly error text hiding technical tracebacks. |
| **Errors** | `error.age_invalid` | `You fail to meet the minimum age requirements of 18 years to utilize this software.` | `⚠️ You must be 18 or older to join.` | Clear policy statement without punitive language. |
| **Errors** | `error.name_invalid` | `The name length provided violates the system bounds constraint of 2-20 characters.` | `⚠️ Name must be 2–20 characters.` | Clear constraint explanation. |
