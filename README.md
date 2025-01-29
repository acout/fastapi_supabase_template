# FastAPI Supbase Template

## Environment

### Python

> [uv](https://github.com/astral-sh/uv) is an extremely fast Python package and project manager, written in Rust.

```bash
cd backend
uv sync --all-groups --dev
```

### [Supabase](https://supabase.com/docs/guides/local-development/cli/getting-started?queryGroups=platform&platform=linux&queryGroups=access-method&access-method=postgres)

install supabase-cli

```bash
# brew in linux https://brew.sh/
brew install supabase/tap/supabase
```

launch supabase docker containers

```bash
# under repo root dir
supabase start
```

> [!NOTE]
> modify the `.env` from the output of `supabase start` or run `supabase status` manually.

## Test

```bash
cd backend
# test connection of db and migration
scripts/pre-start.sh
# unit test
scripts/test.sh
# test connection of db and unit test
scripts/tests-start.sh
```

1. [x] test_main.py
2. [x] test_crud/
