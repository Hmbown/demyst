# Hacker News Launch Strategy

## Post Title (Choose One)

**Option A (Direct):**
> Show HN: Demyst - A linter for scientific logic errors in ML code

**Option B (Problem-focused):**
> Show HN: Demyst - Catches the np.mean() that hides rogue AI agents

**Option C (Comparison):**
> Show HN: Demyst - Like mypy for scientific code (catches data leakage, p-hacking)

## Post URL

https://github.com/Hmbown/demyst

## First Comment (Post immediately after submitting)

---

Hey HN! I built Demyst after a close call with what I call "Computational Mirages."

**The Story:** I was working on an AI safety analysis for an agent swarm. The code looked perfect - average alignment score was 0.999. Ship it, right?

Except... one line of `np.mean()` was hiding a single rogue agent with 0.0 alignment. That agent would have caused a cascade failure. The mean "looked safe" but destroyed the variance information I needed to see the outlier.

**What Demyst catches:**

1. **Computational Mirages** - `mean()`, `sum()` that destroy variance (my original use case)
2. **Data Leakage** - The #1 ML error: fitting scalers before train/test split
3. **P-hacking** - Multiple hypothesis tests without correction
4. **Unit Mismatches** - Adding meters to seconds
5. **Tensor Issues** - Gradient death in deep networks

**How it works:** Demyst uses AST analysis, not regex. It actually understands the semantic structure of your code. When you write `np.mean(x)`, it knows that's a variance-destroying aggregation, not just a string match.

**Quick try:**
```bash
pip install demyst
demyst analyze your_ml_code.py
```

Or try the Colab notebook: [link]

I'd love feedback, especially from ML researchers who've been bitten by these issues. What other "silent scientific errors" should Demyst catch?

---

## Timing Recommendations

- **Best days:** Tuesday-Thursday
- **Best time:** 9-11 AM PST (when US West Coast wakes up, Europe still online)
- **Avoid:** Weekends, holidays, major tech news days

## Response Preparation

**If asked "How is this different from pytest/hypothesis?":**
> pytest tests behavior, hypothesis tests properties. Demyst tests scientific *meaning*. pytest can't tell you that your `mean()` is hiding a critical outlier, because that's mathematically correct code.

**If asked "Won't this have lots of false positives?":**
> We've worked hard on this - the current version has about 37% FP rate on real ML code (down from 80% in early versions). You can also configure domain-specific profiles to adjust sensitivity.

**If asked "Why not just use type hints?":**
> Type hints tell you *what type* a value is, not *what it means scientifically*. A float is a float - type hints can't tell you it's a p-value that needs multiple testing correction.

## Success Metrics

- [ ] Post stays on front page for 2+ hours
- [ ] 50+ points
- [ ] 20+ comments (engagement shows interest)
- [ ] GitHub stars increase
- [ ] PyPI downloads increase
