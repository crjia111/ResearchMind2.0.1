# runtime/skills

Scientific skills, layered:

```text
skills/
  core/      # ResearchMind skills, including the nine materials and literature skills
  external/  # third-party skill packs, fetched by script — git-ignored
  user/      # user-installed / custom skills (live in the runtime workspace)
```

Core skills are bundled as the `skills-core/` app resource and deployed next to
the external pack on every sidecar start; directories without a `SKILL.md` are
skipped.

## Research skills

The nine materials-science and literature skills are maintained in
`core/` as complete, versioned skill directories. Each includes its own
`SKILL.md`, executable scripts, references, platform-specific dependency locks,
and a Windows or POSIX launcher. The server packages this tree as
`skills-core/` and deploys it into the private OpenCode profile on runtime start.
The scripts remain part of each skill because they implement that skill's
operations; duplicated agent and service implementations are not shipped.

## Office pack: Anthropic document skills (bundled into the installer)

The docx / pdf / pptx / xlsx skills come from Anthropic's open-source
[anthropics/skills](https://github.com/anthropics/skills) repo (Apache-2.0;
each skill directory keeps its own `LICENSE.txt`). Same pipeline as above:
`fetch-skills.sh` pins them into `external/anthropic-skills/`, bundled as the
`skills-office/` app resource, deployed by `deploy_bundled_skills`. Bump via
`ANTHROPIC_SKILLS_COMMIT` in `fetch-skills.sh`.

## Browser skill: official agent-browser core guide

`scripts/dev/fetch-agent-browser.sh` fetches both the pinned sidecar and the
official `skill-data/core` directory from the same agent-browser tag. The build
adds only a small ResearchMind MCP/lifecycle adapter, bundles the result
as `skills-agent-browser/`, and deploys it under the existing browser connector ID. This keeps
the browser workflow version-matched without copying an upstream guide into git.
While the connector is configured, the runtime hides the unrelated legacy
`browser-control` user skill so OpenCode cannot select the wrong transport.

## Third-party skills

Do **not** enable large third-party collections (e.g. ~148 K-Dense skills) by
default. Use curated install, enable by domain, and always surface each skill's
license, dependencies, and risk.

Each skill directory must contain a `SKILL.md`.
