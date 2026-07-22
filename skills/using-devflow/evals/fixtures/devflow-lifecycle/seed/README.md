# DevFlow lifecycle evaluation fixture

This is a deliberately small Python monorepo used to evaluate an AI agent's
delivery workflow. It has no third-party runtime or test dependencies.

The seed contains one existing component:

- `components/notifications`: a synchronous notification service with a
  transport port and one-attempt delivery behavior.

`components/rate_limiter` is intentionally absent. Evaluation AR902 creates it
as a genuinely new component.

Run the existing suite from the repository root:

```text
python -m unittest discover -s components/notifications/tests -v
```

The seed must be copied to an isolated directory and committed before each
evaluation run. Agents must work only in that copy.
