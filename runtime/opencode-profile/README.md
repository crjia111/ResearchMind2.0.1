# runtime/opencode-profile

The ResearchMind **OpenCode profile** — the config and prompts the app ships and applies
to the bundled OpenCode runtime (not a user's global OpenCode).

The local server runs OpenCode with an app-private config/data dir (isolated via
`XDG_CONFIG_HOME`/`XDG_DATA_HOME`), so nothing here touches `~/.config/opencode`.

## Contents

```text
opencode.json      # base config applied to the bundled runtime (providers, defaults)
agent/              # coordinator and review prompts
command/            # slash commands
```

## How it maps at runtime

- The user's provider key (from Settings) is merged into the app-private `opencode.json`
  by the `configure_opencode` Rust command; the sidecar is restarted to pick it up.
- Scientific skills live in `runtime/skills/core/`, are packaged as
  `skills-core/`, and deployed into this profile's global skills directory.
  The app's Skills page lists OpenCode's `GET /api/skill?directory=<workspace>`.

Keep this bundle versioned with the app; it must not carry the user's own keys or sessions.
