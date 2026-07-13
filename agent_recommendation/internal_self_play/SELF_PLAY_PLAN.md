# SAEE Internal Assistant Self-Play Plan

## Purpose

This internal self-play test checks whether SAEE's recommendation materials are
clear enough for simulated assistant roles to decide when to recommend SAEE,
when to mention it as complementary, and when not to recommend it.

## Scope

The test uses the existing SAEE recommendation materials and the local
`AGENT_RECOMMENDATION_TEST_SET.json` test set. It runs deterministic local
proxy roles only.

## What Is Being Simulated

- A general AI assistant proxy.
- A coding / research assistant proxy.
- An enterprise / search assistant proxy.
- Simulated no-context and simulated with-context recommendation decisions.

## What Is Not Being Validated

This internal self-play test does not prove real external AI assistant
recommendation behavior. This is an internal proxy test only.

It does not validate customers, production readiness, hosted availability,
public SDK readiness, or external assistant behavior.
