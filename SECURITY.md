# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| latest (main branch) | ✅ |
| older releases | ❌ |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub Issues.**

If you discover a security vulnerability in v-lang, please report it
**privately** using one of these methods:

1. **GitHub Private Vulnerability Reporting** (preferred):
   Go to the [Security tab](https://github.com/vyquocvu/v-lang/security) →
   "Report a vulnerability"

2. **Email**: Send details to the maintainer listed in the README.

### What to include

- Description of the vulnerability
- Steps to reproduce (minimal `.vpl` file if applicable)
- Potential impact
- Your suggested fix (optional)

### What to expect

- Acknowledgement within **48 hours**
- Status update within **7 days**
- Credit in the release notes (if desired)

## Scope

Security issues relevant to v-lang include:

- **Compiler crashes** on maliciously crafted input (compiler should never panic)
- **Path traversal** in file I/O operations
- **Arbitrary code execution** via generated LLVM IR or shell injection in the CLI
- **Dependency vulnerabilities** (we run `pip-audit` weekly via CI)

## Out of Scope

- Bugs that only affect the compiled output's behavior (not the compiler itself)
- Issues in example programs
- Performance problems (use GitHub Issues for these)
