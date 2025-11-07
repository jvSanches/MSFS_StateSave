## MSFS_StateSave — .cfg Authoring Guide

This guide explains how to author configuration files consumed by `prototype/panelStates.py` to save and restore complex aircraft states in Microsoft Flight Simulator using MobiFlight expressions and SimConnect events.

### What this tool does
- Reads a plain-text `.cfg` (human/LLM-authored), queries current values for each line with `value_get=[…]`, and writes a timestamped `.sav` with `value=[…]` prepended.
- Loads from `.sav` or `.cfg` and applies actions described by tokens on each line (sets, toggles, increments/decrements, or events with parameters). It compares current sim values to target values when both `value_get` and a setter are present, acting only when different.

### File format
- One item per line. Lines starting with `#` are comments.
- Tokens are space-separated and can appear in any order on the line.

Recognized tokens:
- `value_get=[<MF expression>]` — read/query the current value from the sim.
- `value_set=[<MF expression>]` — write a value or perform actions; supports placeholder injection and enumerations.
- `value_toggle=[<MF expression>]` — perform a toggle via expression.
- `value_inc=[<MF expression>]` — increment via expression (looped until target reached).
- `value_dec=[<MF expression>]` — decrement via expression (looped until target reached).
- `value_inc_event=[EVENT]` — increment by firing a SimConnect event.
- `value_dec_event=[EVENT]` — decrement by firing a SimConnect event.
- `value_set_event=[EVENT]` — fire a SimConnect event with an integer parameter (target value).

Supporting fields added during save:
- `value=[<number>]` — prepended to lines in `.sav` files to capture the snapshot value.

### MobiFlight expression basics (A:, L:, K:)
- `A:` SimVars (aircraft variables) read-only, optionally writeable when used in this tool with MobiFlight semantics.
- `L:` Local variables specific to the aircraft, commonly boolean or small enumerations; read/write via MobiFlight.
- `K:` Events invoked through SimConnect to perform actions or set indexed values.

Always specify units/types inside expressions so read and write agree exactly, e.g. `Bool`, `Number`, `Feet`, `Degree`, `Frequency BCD16`, etc.

### Placeholders and enumerations
- Placeholder injection: Use `$` inside `value_set` to inject the target value (from `value=[…]` or literal). Example:
  - `value_get=[(L:var_SeatBeltLights, Bool)] value_set=[$ (>L:var_SeatBeltLights, Bool)]`
- Enumerations: Provide multiple `value_set` options separated by `;`. The loader indexes by `int(value)`. Example:
  - `value_get=[(L:Mode, Number)] value_set=[0 (>K:FOO);1 (>K:BAR);2 (>K:BAZ)]`

### Choosing the right pattern
- Simple booleans or numbers (L:Vars): pair `value_get` with `value_set` using `$`.
- Events with a direct parameter: use `value_set_event=[EVENT]` and pass the target (coerced to int) from the saved value.
- Knobs/steppers without direct set: use `value_inc/value_dec` or `value_inc_event/value_dec_event`; the loader loops until `value_get` matches the target.
- Pure actions that should always happen (no comparison): use a single `value_set` line without `value_get`.

### Equality and timing
- Floating-point equality is direct; prefer discrete values or transformations that produce exact results.
- The loader sleeps ~0.1s between actions; avoid very long chains in a single expression.

### Practical examples (from this repo)
1) Direct L:Var boolean
```
value_get=[(L:var_SeatBeltLights, Bool)] value_set=[$ (>L:var_SeatBeltLights, Bool)]
```

2) K: event with side index and parameter injection
```
value_get=[(A:LIGHT LANDING:1, Bool)] value_set=[1 $ (>K:2:LANDING_LIGHTS_SET)]
```

3) Event with parameter (radio frequencies, codes)
```
value_get=[(A:COM ACTIVE FREQUENCY:1, Frequency BCD16)] value_set_event=[COM_RADIO_SET]
```

4) Increment/decrement using events (flaps, trims)
```
value_get=[(A:FLAPS HANDLE INDEX:1, Number)] value_inc_event=[FLAPS_INCR] value_dec_event=[FLAPS_DECR]
```

5) Circuit breaker templates using chained operations
```
value_get=[4 (>A:BUS LOOKUP INDEX, Number) (A:CIRCUIT CONNECTION ON:50, Bool)] value_set=[50 4 (>K:2:ELECTRICAL_BUS_TO_CIRCUIT_CONNECTION_TOGGLE)]
```

See `Starship.cfg` for many working patterns, including multi-circuit templates.

### Writing robust lines
1) Identify the underlying control:
   - Prefer `L:` vars for add-on systems when available.
   - Use `A:` simvars for standard aircraft systems or readbacks.
   - Use `K:` events to actuate changes, especially for standard lights, radios, gear, and trims.
2) Choose a token strategy:
   - Deterministic variable with direct write: `value_get` + `value_set` with `$` and matching unit.
   - Indexed or cyclic control: `value_inc_event/value_dec_event` (or expression variants).
   - Parameterized event: `value_set_event` with target integer.
3) Match units exactly between `value_get` and `value_set`.
4) Use enumeration lists only when the read value maps 1:1 to discrete options.

### Common pitfalls and conventions
- `event_toggle` exists in the parser but is not reliably acted upon; prefer `value_toggle` or paired `*_event` patterns.
- Avoid implicit unit conversions; always specify the unit in both get and set expressions.
- For radios and KOHLSMAN, BCD16/scale conversions are often needed; see working examples in `Starship.cfg`.
- Some manual tables (e.g., `starship_tables_plain_text.txt`) list variables/events that don’t map directly; validate against working examples and adjust.

### Authoring workflow
1) Prototype one control at a time: add a line with `value_get` and a minimal setter.
2) Run save to capture a `.sav` and confirm the `value=[…]` matches expectations.
3) Run load and verify the tool adjusts the sim to the saved value (observe console logs).
4) Iterate: fix units, switch to `*_event` loops if direct sets aren’t reliable, or use enumerations.

### Validation checklist
- Does `value_get` return the expected type and scale at rest and after changes?
- Do `value_set` operations use `$` correctly and the same unit?
- For enumerations, does `int(value)` land on a valid index for all cases?
- For event loops, do increments/decrements converge quickly without overshoot?
- Are long chains split across separate lines to avoid timing issues?

### Cross-references
- Example config: `Starship.cfg` (see sections for lights, radios, trims, and circuit breakers).
- Reference table (raw): `starship_tables_plain_text.txt` — extracted from the aircraft manual. Use it as a starting point; verify each entry against the working examples in `Starship.cfg`.

### Running the tool
- Save state from a `.cfg`:
```
python prototype/panelStates.py Starship.cfg
```
- Load state from a `.sav`:
```
python prototype/panelStates.py path\to\save.sav
```

### Notes for LLMs generating `.cfg` files
- Prefer `value_get + value_set` pairs for deterministic controls; match units.
- Use `$` placeholder to inject values into `value_set` expressions.
- Use `*_event` forms for steppers/knobs; avoid arithmetic when SimConnect events exist.
- Keep lines short and deterministic; avoid side-effect-heavy chains unless necessary.
- Validate against working patterns in `Starship.cfg` before generating large sections.


