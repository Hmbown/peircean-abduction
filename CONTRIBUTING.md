# Contributing to Peircean Abduction

> "Do not block the way of inquiry." — C.S. Peirce

We value rigor, logic, and testability. This project is not just an MCP server; it is an implementation of a specific logical framework. Contributions must adhere to this philosophical strictness.

## ⚡ Rapid Development

We use a `Makefile` to standardize all operations.

```bash
# 1. Install Development Dependencies
make dev

# 2. Run All Checks (Format, Lint, Test, Verify)
make check
```

**Key Commands:**
- `make test`: Run the pytest suite.
- `make lint`: Enforce strict typing (MyPy) and style (Ruff).
- `make verify`: Execute the MCP validation script.
- `make clean`: Remove build artifacts.

## 📐 Architectural Standards

### 1. The 3-Phase Loop
Any changes to the core logic must respect the **Observe → Hypothesize → Evaluate** cycle. See [PEIRCEAN_SPEC.md](docs/PEIRCEAN_SPEC.md) for the canonical definitions.

### 2. Strict Typing
We enforce `mypy --strict` equivalents.
*   **No `Any`**: Unless absolutely necessary.
*   **No Untyped Defs**: All functions must have signatures.

### 3. Commit Protocol
We follow [Conventional Commits](https://www.conventionalcommits.org/).
*   `feat: add new critic persona`
*   `fix: handle empty context in Phase 1`
*   `docs: update IBE scoring criteria`

## 📝 Pull Request Protocol

1.  **Fork & Branch**: `git checkout -b feat/my-logic-upgrade`
2.  **Implement**: Write clean, typed, and documented code.
3.  **Verify**: Run `make check`. **PRs that fail verification will be rejected.**
4.  **Documentation**: Update `PEIRCEAN_SPEC.md` if you modify the schema.

## 🧠 Design Philosophy

*   **Uncertainty is First-Class**: Never return a bare string if you can return a probability distribution.
*   **Hypotheses are Objects**: A hypothesis is not just text; it is an object with `prior_probability`, `testable_predictions`, and `id`.
*   **No Lumping**: If two explanations have different falsification criteria, they are different hypotheses.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.