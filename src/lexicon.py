"""
Hand-built hawkish/dovish phrase lexicon for the word-list tone-scoring method
(PLAN.md Section 3A, Method 2 - following "Parsing the Fed"'s phrase-lexicon
approach). Each entry is a (phrase, topic, sentiment) tuple:
  - phrase: a short phrase typical of FOMC statements/minutes/speeches.
    Matching is bag-of-words within a sentence (a phrase matches if all of
    its words appear anywhere in the sentence), not strict adjacency - this
    mirrors "Parsing the Fed"'s statement that "words in a phrase need not
    be consecutive."
  - topic: one of "interest_rate", "economy", "job_market", "sentiment"
    (general inflation/risk language), matching the reading's topic buckets.
  - sentiment: +1 (hawkish), -1 (dovish). Neutral/direction-free phrases are
    omitted since they don't affect the sign-based scoring formula.

This lexicon is our own construction (the readings only show illustrative
examples, not a published list) - see PLAN.md's noted risk that it needs a
sanity-check pass against a few statements of known tone before trusting it
on the full corpus.
"""

LEXICON = [
    # --- interest_rate: hawkish (rate increases / tightening / restrictive stance) ---
    ("raise the target range", "interest_rate", 1),
    ("raising the target range", "interest_rate", 1),
    ("increase the target range", "interest_rate", 1),
    ("increasing the target range", "interest_rate", 1),
    ("further increases in the target range", "interest_rate", 1),
    ("additional firming", "interest_rate", 1),
    ("additional policy firming", "interest_rate", 1),
    ("further tightening", "interest_rate", 1),
    ("tightening of monetary policy", "interest_rate", 1),
    ("restrictive stance of monetary policy", "interest_rate", 1),
    ("policy remains restrictive", "interest_rate", 1),
    ("higher for longer", "interest_rate", 1),
    ("warrant further increases", "interest_rate", 1),
    ("rate hike", "interest_rate", 1),
    ("hiking rates", "interest_rate", 1),
    ("raise interest rates", "interest_rate", 1),
    ("reduce the size of the balance sheet", "interest_rate", 1),
    ("continuing to reduce its holdings", "interest_rate", 1),
    # --- interest_rate: dovish (rate cuts / easing / accommodative stance) ---
    ("lower the target range", "interest_rate", -1),
    ("lowering the target range", "interest_rate", -1),
    ("decrease the target range", "interest_rate", -1),
    ("reduce the target range", "interest_rate", -1),
    ("cut interest rates", "interest_rate", -1),
    ("rate cut", "interest_rate", -1),
    ("cutting rates", "interest_rate", -1),
    ("easing of monetary policy", "interest_rate", -1),
    ("accommodative stance of monetary policy", "interest_rate", -1),
    ("policy remains accommodative", "interest_rate", -1),
    ("support the economy with lower rates", "interest_rate", -1),
    ("warrant lower rates", "interest_rate", -1),
    ("exceptionally low levels", "interest_rate", -1),
    ("near zero", "interest_rate", -1),
    ("increase its holdings of securities", "interest_rate", -1),
    ("expand the balance sheet", "interest_rate", -1),
    ("asset purchases", "interest_rate", -1),

    # --- economy: hawkish (strong/overheating growth) ---
    ("activity has been expanding at a solid pace", "economy", 1),
    ("economic growth has been strong", "economy", 1),
    ("robust economic growth", "economy", 1),
    ("growth has picked up", "economy", 1),
    ("activity has rebounded strongly", "economy", 1),
    ("growth exceeded expectations", "economy", 1),
    ("economy continues to expand at a solid pace", "economy", 1),
    ("consumer spending has been strong", "economy", 1),
    ("business investment has been strong", "economy", 1),
    # --- economy: dovish (weakening growth) ---
    ("economic activity has slowed", "economy", -1),
    ("growth has moderated", "economy", -1),
    ("activity has weakened", "economy", -1),
    ("downside risks to economic growth", "economy", -1),
    ("activity has decelerated", "economy", -1),
    ("risk of recession", "economy", -1),
    ("growth has slowed further", "economy", -1),
    ("economic downturn", "economy", -1),
    ("consumer spending has slowed", "economy", -1),
    ("business investment has softened", "economy", -1),
    ("considerable risks to the economic outlook", "economy", -1),

    # --- job_market: hawkish (tight labor market) ---
    ("labor market remains tight", "job_market", 1),
    ("job gains have been strong", "job_market", 1),
    ("job gains have been robust", "job_market", 1),
    ("unemployment rate remains low", "job_market", 1),
    ("labor market conditions have continued to strengthen", "job_market", 1),
    ("strong labor demand", "job_market", 1),
    ("labor market is very tight", "job_market", 1),
    ("wage growth has picked up", "job_market", 1),
    ("payroll employment increased strongly", "job_market", 1),
    # --- job_market: dovish (weakening labor market) ---
    ("labor market has cooled", "job_market", -1),
    ("job gains have slowed", "job_market", -1),
    ("unemployment rate has risen", "job_market", -1),
    ("labor market conditions have eased", "job_market", -1),
    ("layoffs have increased", "job_market", -1),
    ("labor demand has softened", "job_market", -1),
    ("labor market has weakened", "job_market", -1),
    ("payroll employment increased modestly", "job_market", -1),
    ("rise in the unemployment rate", "job_market", -1),

    # --- sentiment: hawkish (inflation elevated / rising / upside risks) ---
    ("inflation remains elevated", "sentiment", 1),
    ("inflation pressures have increased", "sentiment", 1),
    ("inflation expectations have risen", "sentiment", 1),
    ("price pressures remain high", "sentiment", 1),
    ("inflation has proven persistent", "sentiment", 1),
    ("upside risks to inflation", "sentiment", 1),
    ("inflation remains well above", "sentiment", 1),
    ("inflation has moved up", "sentiment", 1),
    ("higher inflation", "sentiment", 1),
    ("elevated inflation", "sentiment", 1),
    ("persistently high inflation", "sentiment", 1),
    ("vigilant against inflation risks", "sentiment", 1),
    ("committed to returning inflation to 2 percent", "sentiment", 1),
    ("further progress on inflation may be slow", "sentiment", 1),
    # --- sentiment: dovish (inflation easing / declining / downside risks) ---
    ("inflation has eased", "sentiment", -1),
    ("inflation has declined", "sentiment", -1),
    ("inflation pressures have diminished", "sentiment", -1),
    ("inflation continues to move toward the committee's objective", "sentiment", -1),
    ("price pressures have subsided", "sentiment", -1),
    ("downside risks to inflation", "sentiment", -1),
    ("inflation has come down", "sentiment", -1),
    ("disinflation", "sentiment", -1),
    ("inflation has moderated", "sentiment", -1),
    ("lower inflation", "sentiment", -1),
    ("well anchored", "sentiment", -1),
    ("prepared to adjust the stance of policy as appropriate", "sentiment", -1),
    ("risks have moved into better balance", "sentiment", -1),
    ("act as appropriate to sustain the expansion", "sentiment", -1),
]

TOPICS = sorted({topic for _, topic, _ in LEXICON})
