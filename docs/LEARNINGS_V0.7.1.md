# Engineering Learnings — v0.7.1

## 1. A subsystem is not “automatic” until the live runtime calls it

v0.7.0 correctly implemented adaptive specialist profiles, persistence, scoring, replay, coverage, and routing support. A post-release audit showed that the default API runtime had not yet supplied the adaptive engine to the live router or server learning recorder. The lesson is simple: architecture presence and runtime activation are separate acceptance criteria.

## 2. Live registry membership matters

A specialist profile that exists in code cannot receive missions unless it is registered in the default live Guardian Registry. v0.7.1 therefore adds the ten elite specialist profiles to the live registry while preserving the original 30-role architecture team.

## 3. Automatic success learning needs stronger evidence than automatic failure learning

A concrete provider error, policy denial, tool error, or max-step event is objective evidence that something failed. A final answer saying “done” is not objective evidence that something succeeded. Successful specialist learning therefore requires a recorded verification tool result.

## 4. Self-reinforcing success would corrupt routing

If Guardians could improve their routing score simply by returning a successful-looking final answer, a confident but unreliable specialist could progressively route more work to itself. Requiring verification evidence prevents that positive-feedback failure mode.

## 5. Persistent state must be a first-class runtime setting

Adaptive learning is useful only if it survives process restarts and can be isolated between environments. `NEXUS_ADAPTIVE_INTELLIGENCE_PATH` makes that persistence explicit and testable.

## 6. Version metadata is part of correctness

The live API was still reporting an old hard-coded version even though package and plugin versions had advanced. Runtime version reporting now derives from package `__version__`, reducing future drift.

## 7. Compatibility can coexist with specialization

The existing mission classifier uses broad capabilities such as backend, testing, devops, security, and AI engineering. Instead of breaking that contract, specialist profiles receive routing aliases that bridge those broad mission capabilities to richer specialist capabilities.

## 8. “Gets smarter every time” should mean verified compounding evidence

The production interpretation is now:

```text
run
  ↓
objective verification or concrete failure
  ↓
automatic per-skill evidence update
  ↓
confidence / trend / weakness changes
  ↓
routing and training priorities adapt
  ↓
future work benefits from prior verified outcomes
```

That is genuine system-level adaptation without claiming live model-weight retraining or allowing uncontrolled self-modification.
