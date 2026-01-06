# Embedded Service Pattern Documentation
## P3.2B.2 Infrastructure Pattern Template

**Created**: January 5, 2026  
**Purpose**: Document proven embedded service pattern from P3.2A success for future service creation  
**Authority**: Template for all future service implementations

---

## Proven Pattern from P3.2A

### Success Examples
- ✅ `common/time.py` + `common/concrete_time_service.py` - TimeService
- ✅ `common/ids.py` + `common/concrete_id_service.py` - IDService
- ✅ `src/app/core/db/database.py` - Database service
- ✅ `src/app/core/logger.py` - Basic logging service

### Pattern Benefits
- **Zero Circular Imports**: Abstract interface + concrete implementation in same file
- **Clean Dependencies**: Canonical service instance export
- **Standards Compliance**: Follows Standards.md requirements
- **Proven Stability**: No runtime failures in P3.2A implementation

---

## Service Creation Template

### File Structure Pattern
```
common/
├── service_name.py          # Abstract interface + embedded concrete + canonical instance
└── concrete_service_name.py # Optional: Separate concrete if complex
```

### Code Template
```python
# common/new_service.py
from abc import ABC, abstractmethod
from typing import Any

class NewService(ABC):
    """Abstract interface for new service functionality."""
    
    @abstractmethod
    def operation(self, param: str) -> Any:
        """Service operation description."""
        pass

class ConcreteNewService(NewService):
    """Embedded concrete implementation."""
    
    def operation(self, param: str) -> Any:
        # Implementation here
        return result

# Canonical instance for system-wide use
new_service = ConcreteNewService()
```

### Import Pattern
```python
# In client code - ALWAYS use canonical instance
from common.new_service import new_service

# NEVER instantiate directly
# new_service = ConcreteNewService()  # WRONG
```

---

## Service Integration Checklist

### Required Components
- [ ] Abstract interface class with clear method signatures
- [ ] Embedded concrete implementation class
- [ ] Canonical service instance variable
- [ ] Type hints for all methods
- [ ] Documentation strings for interface

### Standards.md Compliance
- [ ] No direct `datetime.now()` usage (use TimeService)
- [ ] No direct `uuid.uuid4()` usage (use IDService)
- [ ] Follows logging patterns if applicable
- [ ] Uses dependency injection where appropriate

### Testing Requirements
- [ ] Service instantiates without errors
- [ ] All abstract methods implemented
- [ ] No circular import issues
- [ ] Integration with existing services works

---

## Anti-Patterns to Avoid

### Import Issues
```python
# WRONG - Creates circular imports
from some_module import ConcreteService
service = ConcreteService()

# RIGHT - Use canonical instance
from common.service import service
```

### Direct Instantiation
```python
# WRONG - Multiple instances, inconsistent state
service1 = ConcreteService()
service2 = ConcreteService()

# RIGHT - Single canonical instance
from common.service import service
```

### Abstract Class Usage
```python
# WRONG - Cannot instantiate abstract class
from common.service import Service
service = Service()  # TypeError

# RIGHT - Use concrete canonical instance
from common.service import service
```

---

## Future Service Implementation Guide

### When Creating New Services
1. **Copy this template** to `common/new_service.py`
2. **Define abstract interface** with clear method signatures
3. **Implement concrete class** embedded in same file
4. **Create canonical instance** at module level
5. **Test import patterns** to prevent circular dependencies
6. **Validate Standards.md compliance** before integration

### Integration Points
- Document lifecycle operations (P3.2B.2 scope)
- Monitoring and analytics (P3.2B-Gamma scope)
- Resource optimization (P3.2B-Delta scope)
- Any future services requiring consistent patterns

This pattern enables reliable service creation without the circular import and instantiation issues that affected earlier development phases.