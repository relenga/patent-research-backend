# Template Repository Addition for README.md

## FastAPI Governed AI Template

This repository is a **governed FastAPI + AI project template** that provides:

- **Phase 0 (Bootstrap):** Environment verification and toolchain setup
- **Phase 1 (Prune):** Cleaned FastAPI boilerplate with external infrastructure removed
- **Phase 2 (Harden):** Complete contract and interface system for AI development

### What's Included

✅ **Clean FastAPI Backend** - No unused template features, safe defaults  
✅ **AI Agent Governance** - Governance.md for controlled AI-assisted development  
✅ **Phase Discipline System** - BuildPlan.md with structured development phases  
✅ **Service Contracts** - Abstract interfaces for common services, pipelines, state management  
✅ **API Standards** - Routing invariants, response envelopes, error handling contracts  
✅ **Development Safety** - Backend lifecycle rules, terminal management, phase enforcement  

### What's NOT Included

❌ **Phase 3+ Implementations** - OCR, vectorization, LLM integration must be implemented per project needs  
❌ **Business Logic** - Service implementations, pipeline orchestration, concrete features  
❌ **Production Config** - Deployment, monitoring, database-specific settings  

## Using This Template

### 1. Create New Project from Template
```bash
# Clone the template
git clone https://github.com/your-org/fastapi-governed-ai-template.git your-project-name
cd your-project-name

# Remove template origin
git remote remove origin

# Add your project's origin
git remote add origin https://github.com/your-org/your-project-name.git
```

### 2. Customize for Your Project
- Update `pyproject.toml` with your project name and metadata
- Update `src/app/core/config.py` APP_NAME and related settings
- Modify `docs/PRD.md` to define your Phase 3+ requirements
- Update `README.md` to describe your specific project

### 3. Maintain Phase Discipline
- **Follow BuildPlan.md** for structured development
- **Respect Governance.md** for AI-assisted development
- **Start with Phase 3 planning** before implementation
- **Use Governance.md** for development environment safety

## Phase 3+ Development

This template provides the **structure** for AI-powered applications. You must:

1. **Plan Phase 3** according to your project requirements
2. **Implement concrete services** using the abstract interfaces from Phase 2
3. **Add business logic** to pipeline steps and state machine execution
4. **Integrate external services** (OCR, LLM APIs, vector databases) as needed

## Support

- **Phase Discipline:** Follow the BuildPlan.md task structure
- **AI Governance:** Enforce Governance.md during development  
- **Development Safety:** Use Governance.md for environment management

---

**Template Version:** Phase 2 Complete (`phase-2-harden-complete`)  
**Last Updated:** December 2025