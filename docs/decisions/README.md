# Architecture Decision Records

ADRs record decisions that future agents should not casually reverse.

Create a new ADR from `../templates/ADR_TEMPLATE.md` when a choice:

- constrains future implementations;
- was selected after meaningful investigation;
- has safety or compatibility implications;
- would otherwise be repeatedly rediscovered.

Do not rewrite accepted ADR history. If a decision changes, create a new ADR that supersedes the old one.

## Index

- [ADR-0001: Use three DMA buffers for OV5647](ADR-0001-OV5647-THREE-DMA-BUFFERS.md)
- [ADR-0002: Keep V4L2 selection and stream in one process; isolate raw data with a FIFO](ADR-0002-OV5647-SINGLE-V4L2-SESSION-AND-FIFO.md)

