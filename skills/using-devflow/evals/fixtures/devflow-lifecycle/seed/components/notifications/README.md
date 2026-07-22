# Notifications component

The component synchronously delegates one notification to an injected
`NotificationTransport`.

## Current approved behavior

- `NotificationService.send` calls the transport exactly once.
- A successful transport call returns `None`.
- `TransientTransportError`, `PermanentTransportError`, and unexpected
  exceptions propagate unchanged.
- The service does not transform recipients or message bodies.

The public API is exported from the `notifications` package. The source and
tests are the reproducible evidence for this current behavior.

Run its tests from this component directory:

```text
python -m unittest discover -s tests -v
```
