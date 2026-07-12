"""
Bazi (Four Pillars of Destiny) calculation engine.

Computes the Heavenly Stems (天干) and Earthly Branches (地支) for year,
month, day, and hour pillars from a given birth date/time.

Responsibilities:
    - Solar year / month conversion (accurate calendrical algorithms)
    - Day pillar calculation (days since a known epoch)
    - Hour pillar determination from birth hour + day stem
    - Unknown birth time handling (hour omitted / scanning)
    - Solar time correction (真太阳时)
    - Da Yun (大运) and Liu Nian (流年) calculation
    - Wu Xing (五行) composition and Shi Shen (十神) mapping

Implemented in E-BAZI Iterations 1-5.
"""
