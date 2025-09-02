error_handler/
├── __init__.py
├── main.py                    # Main entry point and graph builder
├── config.py                   # Configuration and constants
├── types.py                    # Type definitions and enums
├── nodes/                      # LangGraph node functions
│   ├── __init__.py
│   ├── validation.py          # Input validation nodes
│   ├── classification.py      # Error classification nodes
│   ├── analysis.py            # RCA analysis nodes
│   ├── recovery.py            # Recovery strategy nodes
│   ├── messaging.py           # Message generation nodes
│   └── telemetry.py           # Telemetry and feedback nodes
├── services/                   # Core services
│   ├── __init__.py
│   ├── cache.py              # Cache service
│   ├── idempotency.py        # Idempotency checker
│   ├── validator.py          # Input validator
│   └── router.py             # Feedback router
├── tools/                      # Analysis and recovery tools
│   ├── __init__.py
│   ├── classifier.py          # Error classifier tool
│   ├── rca_engine.py          # Root cause analysis engine
│   ├── synonym_mapper.py      # Synonym mapping service
│   ├── recovery_policy.py     # Recovery policy engine
│   └── message_generator.py   # Message generation tool
├── utils/                      # Utility functions
│   ├── __init__.py
│   ├── logging.py            # Logging configuration
│   └── helpers.py            # Helper functions
└── examples/                   # Example usage
    ├── __init__.py
    └── demo.py               # Demo script