# Developer Guide

This guide explains how to maintain `script.oppo203.iso.external` without destabilizing the v2.9.10 Final software-verified baseline.

## Read first

1. [Architecture](architecture.md)
2. [Testing](testing.md)
3. [Packaging](packaging.md)
4. [Release Process](release-process.md)
5. [Code Quality](code-quality.md)
6. [Continuous Integration](ci.md)
7. [AI Maintainer Rules](ai-maintainer-rules.md)

## Core rule

GitHub-readiness builds must not change runtime behavior. They prepare the repository for public collaboration while preserving the verified v2.9.10 Final behavior.
