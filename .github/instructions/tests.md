---
name: "Test-Writer"
description: "Help with writing automated tests"
applyTo: "tests/**/*.py"
---

# Comments

- Do not write comments
- Only allowed comments are `given`, `when`, `then` which split test on sections

# Structure
- In unit/ directory only unit tests allowed.
- In component/ directory  only component tests allowed.

# Stubs
- Use pytest, pytest-mock
- For mocking use MockFixture
- Prefer using for mocking mocker.patch.object

# Parameters
- For multiple cases prefer using parameters. As final parameter use `expected` with result to check

# Asserts
- in assert RHS is expected value