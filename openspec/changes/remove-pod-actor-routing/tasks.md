## 1. Implementation
- [ ] Remove pod/actor routing logic and parameters from `clx/core.py`
- [ ] Remove pod/actor config from `.env` and `.env.example`
- [ ] Remove pod/actor docs and examples from `README.md`
- [ ] Remove pod/actor references from `clx_cli.egg-info/PKG-INFO`
- [ ] Update `openspec/project.md` to remove pod/actor mentions

## 2. Verification
- [ ] Smoke-check `clx_query` to ensure `/v1/query` path is still used by default
- [ ] Ensure docs mention only the `/v1/query` contract
