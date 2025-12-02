---
description: Interactive scientific integrity challenge - test your skills at spotting bugs!
arguments:
  - name: type
    description: Challenge type (leakage, mirage, phacking, or random)
    required: false
---

Start an interactive scientific integrity challenge.

## Instructions

1. Select a challenge type:
   - `leakage` - Data leakage detection
   - `mirage` - Computational mirage detection
   - `phacking` - P-hacking / statistical validity
   - `random` (default) - Surprise me!

2. Present the challenge:
   - Show the buggy code from `.claude-plugin/examples/challenge_<type>.py`
   - Ask the user to spot the bug WITHOUT running demyst first
   - Give them hints if they struggle

3. After they guess (or give up):
   - Run demyst on the challenge file
   - Show what demyst detected
   - Explain WHY it's a problem and the scientific impact
   - Show the corrected code

4. Score and encourage:
   - If they got it right: "🎉 Excellent! You have good scientific intuition!"
   - If they needed hints: "👍 Good effort! This is a tricky one."
   - If they gave up: "No worries! These bugs are subtle. Now you know what to look for."

5. Offer next challenge or resources:
   - "Want to try another? /demyst-challenge <type>"
   - "Read more in the Hall of Shame: README.md"

## Example Flow

```
User: /demyst-challenge

Claude: 🧪 **Scientific Integrity Challenge: The Preprocessing Leak**

Here's some ML code. It trains a model with 95% test accuracy!
But there's a subtle bug that makes the results unreliable.

[Shows challenge code]

Can you spot the data leakage bug?
Take your time - don't peek at the solution yet!

Hint 1: Look at the ORDER of operations.
Hint 2: What data is the scaler trained on?

What do you think the bug is?

User: [guesses]

Claude: Let's see what demyst found...
[runs demyst analyze]

🔍 **Demyst Detection:**
Line 12: fit_transform() called before train_test_split()

**Why This Matters:**
[explains data leakage and inflated metrics]

**The Fix:**
[shows corrected code]

🎉 Great job! Want another challenge? Try /demyst-challenge phacking
```
