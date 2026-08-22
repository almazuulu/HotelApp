#!/usr/bin/env node
/**
 * Single entry point for OpenAPI DTO generation and freshness checks.
 *
 * The schema source is resolved in this order:
 *   1. a positional argument (URL or local file, e.g. `../schema.json` in CI);
 *   2. the OPENAPI_SCHEMA_URL environment variable;
 *   3. the Compose-internal backend URL, so `docker compose exec frontend
 *      npm run generate:api-types` keeps working without configuration.
 *
 * `--check` is forwarded to openapi-typescript: it regenerates in memory,
 * compares with the committed file and exits non-zero on any drift.
 */
import { spawnSync } from 'node:child_process'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const DEFAULT_SCHEMA_URL = 'http://backend:8000/api/v1/schema/?format=json'
const OUTPUT_PATH = 'src/shared/api/generated/schema.d.ts'

const frontendRoot = join(dirname(fileURLToPath(import.meta.url)), '..')
const args = process.argv.slice(2)
const check = args.includes('--check')
const source =
  args.find((arg) => !arg.startsWith('--')) ?? process.env.OPENAPI_SCHEMA_URL ?? DEFAULT_SCHEMA_URL
const cli = join(frontendRoot, 'node_modules', 'openapi-typescript', 'bin', 'cli.js')

const result = spawnSync(
  process.execPath,
  [cli, source, '-o', join(frontendRoot, OUTPUT_PATH), ...(check ? ['--check'] : [])],
  { cwd: frontendRoot, stdio: 'inherit' },
)

process.exit(result.status ?? 1)
