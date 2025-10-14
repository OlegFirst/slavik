# Runtime Components - Deprecated 2025-10-11

## service-catalog-integrated-to-service-discovery

**Status**: ✅ Fully integrated into `/infrastructure/runtime/service-discovery`

**Deprecated**: October 11, 2025

**Reason**: Service Catalog has been fully integrated into Service Discovery v2.0

### Migration Details

The service-catalog component has been integrated into service-discovery through:

1. **catalog_integration.py** - Loads service-catalog.yaml and provides unified view
2. **Service Discovery v2.0 API** - `/v2/catalog/*` endpoints
3. **UnifiedService model** - Combines static catalog + dynamic runtime data

### Integration Points

Service Discovery now provides:
- Static service templates from `service-catalog.yaml`
- Dynamic runtime data from service registry
- Unified view combining both sources
- Database persistence for historical data

### What Was Moved

```
/infrastructure/runtime/service-catalog/
├── service-catalog.yaml     → Still used by service-discovery
├── service-catalog.json     → Reference copy
├── INFRASTRUCTURE_CATALOG.md → Documentation (archived)
└── README.md                → Documentation (archived)
```

### New Location

Service Catalog functionality is now in:
```
/infrastructure/runtime/service-discovery/
├── catalog_integration.py   ← Loads catalog.yaml
├── main.py                  ← Service Discovery v2.0
└── eventbus_integration.py  ← Event broadcasting
```

### service-catalog.yaml Location

The `service-catalog.yaml` file is still used from its original location:
```
/Users/MD/AI-Platform-ISO/infrastructure/runtime/service-catalog/service-catalog.yaml
```

The `catalog_integration.py` automatically finds it using standard search paths.

**Alternative**: You can copy `service-catalog.yaml` to `/infrastructure/runtime/service-discovery/` if preferred.

### API Changes

**Old (service-catalog standalone)**:
- No runtime API
- Static YAML/JSON files only

**New (integrated in service-discovery)**:
```
GET /v2/catalog/services        # All services (catalog + runtime)
GET /v2/catalog/missing         # Services in catalog but not running
GET /v2/catalog/unknown         # Services running but not in catalog
GET /v2/catalog/stats           # Catalog statistics
```

### EventBus Integration

Service Discovery v2.0 publishes events:
- `platform.monitoring.service_registered`
- `platform.monitoring.service_disconnected`
- `platform.monitoring.critical_timeout`

MIO Manager (EYES) subscribes to these events for observation.

### References

- Service Discovery v2.0: `/infrastructure/runtime/service-discovery/`
- MIO Manager Integration: `/infrastructure/AI-office-infrastructure/mio-manager/`
- Event Handlers: `/infrastructure/AI-office-infrastructure/mio-manager/event_handlers.py`

---

**Archive Date**: October 11, 2025
**Archived By**: AI Assistant (Phase 2.1 - MIO EYES Implementation)
