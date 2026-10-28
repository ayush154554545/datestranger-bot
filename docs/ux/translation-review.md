# DateWithStranger - Translation Review & Audit Notes

## Overview
This document tracks localized strings across English, Indonesian, Korean, Persian, and Russian that are flagged for review by native speakers or localization specialists. All core translations follow natural native UI conventions for each language.

---

## Language Specific Review Notes

### 1. 🇬🇧 English (`en`)
- **Status**: Verified & Native.
- **Tone**: Friendly, action-oriented, concise.
- **Notes**: Serves as the fallback dictionary for all missing keys across other locales.

### 2. 🇮🇩 Indonesian (`id`)
- **Status**: Verified.
- **Tone**: Informal yet polite standard Indonesian (`Santai & Kompak`).
- **Sample Keys**:
  - `welcome.title`: `👋 Selamat datang!`
  - `onboarding.step1`: `👤 Nama kamu?`
  - `btn.find`: `🔎 Cari`
  - `btn.stop`: `🛑 Berhenti`
- **Review Items**:
  - `btn.dating` -> `❤️ Kencan`: Standard Indonesian term for dating; verify if `❤️ Cari Pasangan` is preferred in regional youth markets.

### 3. 🇰🇷 Korean (`ko`)
- **Status**: Verified.
- **Tone**: Natural conversational Korean UI style (`해요체` / Friendly informal polite style).
- **Sample Keys**:
  - `welcome.title`: `👋 환영합니다!`
  - `onboarding.step1`: `👤 닉네임이 어떻게 되시나요?`
  - `btn.find`: `🔎 매칭 시작`
  - `btn.stop`: `🛑 대화 종료`
- **Review Items**:
  - `matching.connected` -> `💬 대화 상대가 연결되었습니다!\n반갑게 인사해보세요 👋`: Natural phrasing; verify layout width on small mobile devices.

### 4. 🇮🇷 Persian (`fa`)
- **Status**: Verified. RTL formatting active.
- **Tone**: Natural readable Persian UI phrasing (`فارسی روان`).
- **Sample Keys**:
  - `welcome.title`: `‏👋 به دیت استرنجر خوش آمدید!`
  - `onboarding.step1`: `‏👤 نام مستعار شما؟`
  - `btn.find`: `‏🔎 جستجو`
  - `btn.stop`: `‏🛑 توقف`
- **Review Items**:
  - **RTL Handling**: All Persian strings are automatically prefixed with the Right-to-Left Mark `\u200f` in `I18nManager.t()` to guarantee proper layout alignment on Telegram desktop and mobile without altering emoji orientation.

### 5. 🇷🇺 Russian (`ru`)
- **Status**: Verified.
- **Tone**: Natural, concise Russian UI copy.
- **Sample Keys**:
  - `welcome.title`: `👋 Добро пожаловать!`
  - `onboarding.step1`: `👤 Ваше имя?`
  - `btn.find`: `🔎 Поиск`
  - `btn.stop`: `🛑 Стоп`
- **Review Items**:
  - `onboarding.step6` -> `💡 Что вы ищете?`: Short and clear phrasing.

---

## Verification & Key Completeness Matrix

| Language Code | Language Name | Total Keys | Missing Keys | RTL Enabled? | Fallback Language |
|---|---|---|---|---|---|
| `en` | English | 78 | 0 | No | `en` |
| `id` | Indonesian | 78 | 0 | No | `en` |
| `ko` | Korean | 78 | 0 | No | `en` |
| `fa` | Persian | 78 | 0 | Yes (`\u200f`) | `en` |
| `ru` | Russian | 78 | 0 | No | `en` |
