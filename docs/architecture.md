# Architecture and Design

This document outlines the architecture and design decisions for the MF Holdings Tracker.

## Overview

The system follows a clean architecture with clear separation of concerns:
- **Ingestion**: Fetches raw data from AMCs/AMFI
- **Parsing**: Normalizes AMC-specific formats to standard schema
- **Storage**: Manages database operations via repository pattern
- **Analytics**: Generates insights and aggregations
- **API**: FastAPI endpoints for external access
- **Exporters**: Outputs to Google Sheets and CSV

## Key Patterns

1. **Parser Inheritance**: All AMC parsers extend BaseAMCParser
2. **Repository Pattern**: All DB access through repository classes
3. **Config-Driven**: funds.yaml is the source of truth
4. **Fact Table Design**: One row per fund × stock × month

See the main mf_tracker_architecture.md for detailed design documentation.
