# ADR 005: Telegram Bot Framework Strategy

## Context
The legacy application uses `pyTelegramBotAPI` (TeleBot) in `bot.py`.

## Decision
Retain `pyTelegramBotAPI` for Phase 0/1 initialization and refactoring while isolating Telegram event handlers from core domain logic. Evaluate `aiogram` for future async high-concurrency event loops.

## Alternatives Considered
- Immediate framework rewrite to aiogram: Introduces unnecessary regression risks before baseline clean architecture is established.

## Consequences
- Preserves working Telegram API call contracts while decoupling handlers into clean application layers.

## Status
ACCEPTED
