# TouchDesigner Project Workspace

This directory is the TouchDesigner project root for the Environment Portfolio Platform.
Embody (Envoy MCP) looks for `.toe` files here and generates `.mcp.json`, `AGENTS.md`, and `CLAUDE.md` automatically.

## Quick Start

1. Open TouchDesigner 2025.32820+
2. Create new project → Save as `_TouchDesigner/florawish_sanctuary.toe`
3. Download Embody from: https://github.com/dylanroscover/Embody/releases/latest
4. Drag `Embody-v6.*.tox` into the project
5. Toggle `Envoyenable` on the Embody COMP
6. Verify Envoy MCP on `localhost:9870`
7. Tag networks for externalization (lctrl + lctrl on any COMP/DAT)
8. Export networks via Ctrl+Shift+U → creates `.tdn` files in `networks/`

## Directory Structure

```
_TouchDesigner/
├── florawish_sanctuary.toe    ← Master TD project (create this)
├── components/                ← Reusable .tox components
│   ├── nikki_post_fx.tox
│   ├── nikki_particles.tox
│   ├── melusina_audio.tox
│   └── osc_router.tox
├── networks/                  ← TDN-exported networks (git-versioned)
│   ├── nikki_post_fx.tdn
│   ├── nikki_particles.tdn
│   ├── melusina_audio.tdn
│   └── osc_routing.tdn
├── shaders/                   ← GLSL prototypes
│   ├── toon_nikki.glsl
│   ├── toon_madoka.glsl
│   ├── toon_celestial.glsl
│   └── toon_itto.glsl
└── exports/                   ← Rendered outputs, screenshots
```

## Nikki Aesthetic Reference

See `Docs/NIKKI_VERTICAL_SLICE_PLAN.md` Section 2 for the complete Nikki color bible,
material presets, post-processing specs, and particle style guide.

## MCP Integration

The `.mcp.json` at the EnvironmentPortfolio root registers all three MCP servers:
- Envoy (TD): `localhost:9870`
- Monolith (UE): `localhost:9316`
- Blender MCP: `localhost:9877`
