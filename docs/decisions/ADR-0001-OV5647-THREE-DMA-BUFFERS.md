# ADR-0001: Use Three DMA Buffers for OV5647 Capture

- Status: Accepted
- Date: 2026-08-23

## Context

The Allwinner `sunxi-vin` vendor stack was unstable during early continuous capture attempts. The working snapshot implementation used three MMAP buffers, while failing generic pipelines could request four or more.

## Decision

All OV5647 capture tools in this workspace must request exactly three MMAP buffers unless a new bounded experiment explicitly evaluates another value:

```bash
--stream-mmap=3
```

## Evidence

A bounded 10000-frame capture completed at approximately 31.27 FPS using three cyclic buffers, without DMA, IOMMU, panic, or watchdog errors.

## Consequences

- The HTTP server rejects configuration values other than three buffers.
- Generic GStreamer pipelines must not be assumed safe because they may negotiate their own buffer count.
- A future change requires a new experiment report and an ADR that supersedes this decision.

