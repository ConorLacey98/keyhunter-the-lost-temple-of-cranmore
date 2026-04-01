# keyhunter-the-lost-temple-of-cranmore
A Python text adventure game. Originally written in Python 2 and refactored to Python 3. Features a Textual TUI with persistent inventory, scrollable narrative, and a live status bar. The goal is to survive and collect all 4 skeleton keys.

## Requirements

- Python 3.10+
- [Textual](https://github.com/Textualize/textual) — installed in the project venv

## Setup

```bash
# Create and activate the virtual environment (first time only)
python -m venv keyhunter
keyhunter\Scripts\activate

# Install dependencies
pip install textual
```

## How to run

**Must be run in an external terminal** (Windows Terminal or PowerShell). Textual does not render inside VS Code's integrated terminal.

```bash
# From the project directory
.\keyhunter\Scripts\python keyhunter.py
```

Or with the venv activated:

```bash
python keyhunter.py
```

## Cheat sheet

1. **West** → Forest → **Left** → Manor → Check shed *(crowbar)*
2. Try back door (crowbar required) → Kitchen *(matches picked up automatically)*
3. Living room → *(machete + journal/grave clue)*
4. Leave manor → Forest → **Straight** → Graveyard → dig 5x → *(skeleton key — forest)*
5. Back to crossroads → **North** → Town → **Right** → Burnt house → *(ornate key)*
6. **Left** → Church (ornate key opens it) → *(skeleton key — town)*
7. Back to crossroads → **South** → Mine → Search for light → light torch
8. Mine collapse → Routes → Spider-web **or** Mine cart (both work) → *(pickaxe + diving gear)*
9. Elevator escape → Spider fight → **use pickaxe** → *(skeleton key — mine)* → Lake → *(skeleton key — lake)*
10. Back to crossroads → **West** → Forest → **Right** → Temple (machete + all 4 keys) → **WIN**

### Tips
- The inn restores a life if you are below 3 — worth a detour if you are struggling.
- The church basement is risky without matches (60% chance of slipping). Get matches from the manor kitchen first.
- If you die to the spider, you keep your pickaxe — head back into the mine and try again.

---

## Roadmap — 75 → 100

Features are grouped into three phases. Each phase builds on the last and targets a specific gap in the current ratings.

---

### Textual UI Rework — Next Iteration
*Replace scrolling terminal output with a persistent split-panel TUI using the [Textual](https://github.com/Textualize/textual) framework.*

#### Why Textual over plain Rich

`rich` improves formatting but is still a scrolling output stream — you lose context as text rolls off screen. `textual` gives you a real layout where narrative, inventory, and choices exist as separate persistent regions simultaneously. The game stops feeling like a script and starts feeling like an application.

#### Target layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  Keyhunter: The Lost Temple of Cranmore          ♥ ♥ ♡   Keys: 1/4  │
├────────────────────────────────────┬────────────────────────────────┤
│  THE GRAVEYARD                     │  INVENTORY                     │
│                                    │ ─────────────────────────────  │
│  You walk into the graveyard.      │  ✓  crowbar                    │
│  The graves are overgrown and      │  ✓  matches                    │
│  most tombstones are falling       │  ✓  ornate key                 │
│  apart...                          │  ✓  grave clue                 │
│                                    │  ✓  machete                    │
│  One of the graves catches         │  ✗  skeleton key (town)        │
│  your eye.                         │  ✗  skeleton key (forest)      │
│                                    │  ✗  skeleton key (mine)        │
│       ____                         │  ✗  skeleton key (lake)        │
│      (    )                        │                                │
│      __)(__                        │                                │
│  What you seek lies beneath        │                                │
│                                    │                                │
├────────────────────────────────────┴────────────────────────────────┤
│  [1] Dig into the grave    [2] Leave the graveyard                  │
└─────────────────────────────────────────────────────────────────────┘
```

- **Header** — game title, lives (hearts), keys collected (n/4)
- **Narrative panel** (left, scrollable) — all story text appears here, persists so you can scroll back
- **Inventory panel** (right, static) — always visible, updates reactively when items are picked up
- **Choices bar** (bottom, fixed) — current decision options, always anchored at the bottom

#### Components to build

| Component | Textual widget | Purpose |
|---|---|---|
| `GameHeader` | `Header` | Title + live status (hearts, key count) |
| `NarrativeLog` | `RichLog` | Scrollable narrative, styled text |
| `InventoryPanel` | `Static` + reactive | Always-visible item list |
| `ChoicesBar` | `Horizontal` + `Button` | Current decision options |
| `GameApp` | `App` | Owns layout, drives the game loop |

#### Architecture migration — what changes and what doesn't

**The game logic does not change.** The dispatch table, all `loc_` functions, `inv`, `flags`, `reset_state`, and every line of narrative text are carried over untouched. Only the I/O layer is replaced.

| Current | Textual replacement |
|---|---|
| `print(msg)` | `self.app.narrative.write(msg)` |
| `get_valid_input()` / `prompt_choice()` | `await self.app.get_choice(options)` — posts a message, suspends until player picks |
| `time.sleep(n)` | `await asyncio.sleep(n)` |
| `clear_screen()` | `self.app.narrative.clear()` + update location title |
| `check_inventory()` | Reactive — inventory panel rerenders automatically when `inv` changes |
| `update_inventory()` | Updates `inv` dict → triggers reactive inventory refresh + writes event to narrative |
| `event()` / `warning()` | Rich markup passed to `narrative.write()` — `[yellow]★[/]` / `[red]![/]` |

#### How the async game loop works

Textual apps are async. The game loop becomes a background worker:

```python
async def run_game_loop(self):
    location = "crossroads"
    while location not in ("WIN", "LOSE"):
        handler = LOCATIONS[location]
        location = await handler(self)   # loc_ functions become async, accept app ref
    ...
```

Each `loc_` function becomes `async def loc_crossroads(app)` — same logic, but `print` → `app.narrative.write` and `prompt_choice` → `await app.get_choice(...)`.

#### Migration steps

1. `pip install textual`
2. Build `GameApp` with the three-panel layout (header, narrative+inventory, choices bar)
3. Implement `app.get_choice(options)` — renders buttons in the choices bar, returns the player's pick as a future
4. Convert `loc_` functions to `async def loc_X(app)` — mechanical find/replace of print and input calls
5. Replace `time.sleep` with `await asyncio.sleep`
6. Wire `update_inventory` to push reactive updates to the inventory panel
7. Drop `clear_screen`, `border`, `event`, `warning`, `prompt_choice` — Textual replaces all of them

#### What gets better for free

- Inventory is always visible — no more "I forgot what I'm carrying"
- Narrative is scrollable — read back what you missed without replaying
- Choices are visually distinct from story text at all times
- The status bar (lives, keys) is always present — the tension of `♥ ♡ ♡` is permanent, not just at decision points
- All Phase 1–3 roadmap features slot in cleanly — the NPC dialogue, lore panel, and map all become additional widgets

#### Estimated effort

| Task | Effort |
|---|---|
| Layout scaffold + GameApp | ~3 hours |
| Async game loop + get_choice | ~2 hours |
| Converting all loc_ functions | ~3 hours (mechanical) |
| Reactive inventory panel | ~1 hour |
| Polish (colours, fonts, spacing) | ~2 hours |
| **Total** | **~1–2 focused days** |

---

### Phase 1 — Polish (targets: Code Quality, Fun)
*The game is good. These make it feel finished.*

- **Save / load system** — serialise `inv`, `flags`, and current location to a JSON file so the player can quit and resume. One file per save slot.
- **Colour toggle** — an in-menu accessibility option to disable ANSI codes entirely for terminals that don't support them.
- **Torch timer in the mine** — the torch has a limited life (e.g. 8 moves). A countdown warns the player before it dies, forcing urgency and a decision to push forward or retreat. Matches can relight it once.
- **Temple key-order puzzle** — the four locks require the keys to be inserted in the correct order. The correct order is hinted at by clues scattered across each area (altar inscription, mine engraving, lake carving, grave epitaph). Wrong order resets the sequence but costs nothing — just adds a puzzle layer to what is currently a checkbox.
- **Inventory limit** — the player can only carry 6 items at once. Creates real decisions, especially in the mine where you find two items at once.

---

### Phase 2 — Content (targets: Difficulty, Fun, Sequel Potential)
*The world is interesting. These make it worth exploring.*

- **NPCs with dialogue** — three characters to find across the world:
  - *The Innkeeper* (town inn) — hints at the mine and the temple legend if you ask
  - *The Prospector's Ghost* (mine) — warns you about the spider, gives a cryptic clue about the key order
  - *The Groundskeeper* (graveyard) — knows about D.R., appears only if you have the grave clue
- **Lore collectibles** — optional notes, carvings, and journal pages scattered across every area. Viewable from a new `[L] Lore` option in the menu. Builds out the backstory of Cranmore, D.R., and the temple without putting it in the critical path.
- **Random travel flavour** — short random atmospheric lines when moving between areas ("A crow watches you from the treeline.", "The wind carries the smell of smoke."). Small, but gives the world texture on repeat playthroughs.
- **The Harbour** — a new fifth area accessible from the crossroads. Contains the fifth optional side-quest: find a ship manifest that hints at who built the temple. Reward: a bonus life and a piece of lore.
- **Multiple endings** — the temple ending currently has one outcome. Branch it by what the player did throughout:
  - *Standard ending*: find all keys, enter temple
  - *Lore ending*: find all keys + all lore collectibles — extra scene revealing the full story of D.R.
  - *Speedrun ending*: complete the game under a move count threshold — a short cheeky message acknowledging it

---

### Phase 3 — Depth (targets: Difficulty, Replayability)
*The engine is solid. These make it a different game every time.*

- **Randomised item locations** — on each new game, shuffle which of the four areas holds each skeleton key. The area structure stays the same but the critical path changes. The grave clue still points to the forest key; other keys get their own in-world hints that redirect correctly. High replayability, low implementation cost given the dispatch table architecture.
- **Achievement system** — a local `achievements.json` tracks milestones across all playthroughs: *First Win*, *No Deaths*, *Found All Lore*, *Died to the Basement*, *Beat the Spider First Try*, etc. Viewable from the main menu. No gameplay impact — just satisfying to unlock.
- **Hard mode** — a menu option that applies a set of modifiers simultaneously: 2 starting lives instead of 3, no inn life restore, 75% slip chance in the church basement regardless of matches, spider fight has a 4-second decision timer before it defaults to a wrong choice.
- **Item combinations** — a small crafting layer. Examples: `torch + matches = lit torch` (unlimited mine time), `crowbar + matches = improvised flare` (scares off the spider without a fight). Adds lateral thinking to a game currently built on linear item gates.
- **A proper map** — a `[M] Map` option in the prompt that prints an ASCII map of Cranmore with visited locations marked and unvisited ones shown as `?`. Updates as you explore. Removes the need for the cheat sheet for most players.

---

### Score projection

| Category | Now | After Phase 1 | After Phase 2 | After Phase 3 |
|---|---|---|---|---|
| Difficulty | 52 | 62 | 72 | 90 |
| Fun | 74 | 80 | 92 | 95 |
| Code Quality | 81 | 90 | 90 | 93 |
| Refactorability | 83 | 86 | 86 | 88 |
| Sequel Potential | 83 | 83 | 95 | 97 |
| **Overall** | **75** | **80** | **87** | **93** |

*The remaining 7 points are original content — no amount of engineering fully substitutes for a story people want to tell their friends about.*
