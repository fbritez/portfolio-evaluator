# Logging Instruction

- Whenever a module needs to use a `logger`, import it from `source.utils.logger`.

Example:

```python
from source.utils.logger import logger

logger.info("Starting operation")
```

Rationale:

- Centralizes logging configuration.
- Ensures consistent formatting and handlers across the application.
