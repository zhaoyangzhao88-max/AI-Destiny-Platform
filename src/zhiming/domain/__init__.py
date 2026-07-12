"""
Domain layer.

Contains pure domain entities, value objects, and enumerations with zero
external dependencies. This layer is the heart of the business model.

Entities:
    User        — Aggregate root for user identity and profile
    BaziChart   — Four Pillars chart with pillar values
    Report      — Life analysis report with tiered data

Value Objects:
    Pillar          — Single pillar (year/month/day/hour)
    FiveElements    — Wu Xing element calculations
    TenGod          — Shi Shen (十神) relationships
    DataTier        — Confidence tier (fact / inference / pending)

Enums & State Machines:
    TaskState       — Task lifecycle states
    AnalysisStep    — AI analysis pipeline steps
    DataConfidence  — Data reliability tiers

Implemented in E-DOMAIN Iterations 1-3.
"""
