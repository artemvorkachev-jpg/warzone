#!/usr/bin/env python3
"""Patch enemy droid and structure minimap dots in the pinned Warzone 2100 source."""
from pathlib import Path

p = Path("src/src/radar.cpp")
s = p.read_text(encoding="utf-8")
if "MINIMAP_ENEMY_ALERTS_PATCH" in s:
    raise SystemExit("Alert patch marker already exists; refusing to silently skip patch verification")

needle = """\tbool blinkState = (gameTime - lastBlink) / BLINK_HALF_INTERVAL;

\t/* Show droids on map - go through all players */"""
replacement = """\tbool blinkState = (gameTime - lastBlink) / BLINK_HALF_INTERVAL;

\t// MINIMAP_ENEMY_ALERTS_PATCH: highlight enemy droids and structures only.
\tint hostileObjectsRemaining = 0;
\tfor (UBYTE player = 0; player < MAX_PLAYERS; ++player)
\t{
\t\tif (player == selectedPlayer || aiCheckAlliances(selectedPlayer, player)) continue;
\t\tfor (const DROID* droid : apsDroidLists[player]) { (void)droid; ++hostileObjectsRemaining; }
\t\tfor (const STRUCTURE* structure : apsStructLists[player]) { (void)structure; ++hostileObjectsRemaining; }
\t}
\tconst bool lowMissionTime = mission.time >= 0
\t\t&& gameTime >= mission.startTime
\t\t&& mission.time - static_cast<SDWORD>(gameTime - mission.startTime) < 5 * 60 * GAME_TICKS_PER_SEC;
\tconst bool minimapAlert = lowMissionTime || hostileObjectsRemaining < 10;

\t/* Show droids on map - go through all players */"""
if needle not in s:
    raise SystemExit("Unsupported radar.cpp: DrawRadarObjects anchor not found")
s = s.replace(needle, replacement, 1)

needle = """\t\t\t\telse
\t\t\t\t{
\t\t\t\t\tif (psDroid->selected && !blinkState)
\t\t\t\t\t\tradarOverlayBuffer[pos] = applyAlpha(playerCol, OVERLAY_OPACITY).rgba();
\t\t\t\t\telse
\t\t\t\t\t\tradarOverlayBuffer[pos] = playerCol.rgba();
\t\t\t\t}"""
replacement = """\t\t\t\telse
\t\t\t\t{
\t\t\t\t\tif (minimapAlert && clan != selectedPlayer && !aiCheckAlliances(selectedPlayer, clan))
\t\t\t\t\t\tradarOverlayBuffer[pos] = WZCOL_YELLOW.rgba();
\t\t\t\t\telse if (psDroid->selected && !blinkState)
\t\t\t\t\t\tradarOverlayBuffer[pos] = applyAlpha(playerCol, OVERLAY_OPACITY).rgba();
\t\t\t\t\telse
\t\t\t\t\t\tradarOverlayBuffer[pos] = playerCol.rgba();
\t\t\t\t}"""
if needle not in s:
    raise SystemExit("Unsupported radar.cpp: droid color anchor not found")
s = s.replace(needle, replacement, 1)

needle = """\t\t\t\telse
\t\t\t\t{
\t\t\t\t\tif (psStruct->player == selectedPlayer && psStruct->selected && !blinkState)
\t\t\t\t\t\tradarOverlayBuffer[pos] = applyAlpha(playerCol, OVERLAY_OPACITY).rgba();
\t\t\t\t\telse
\t\t\t\t\t\tradarOverlayBuffer[pos] = playerCol.rgba();
\t\t\t\t}"""
replacement = """\t\t\t\telse
\t\t\t\t{
\t\t\t\t\tif (minimapAlert && clan != selectedPlayer && !aiCheckAlliances(selectedPlayer, clan))
\t\t\t\t\t\tradarOverlayBuffer[pos] = WZCOL_YELLOW.rgba();
\t\t\t\t\telse if (psStruct->player == selectedPlayer && psStruct->selected && !blinkState)
\t\t\t\t\t\tradarOverlayBuffer[pos] = applyAlpha(playerCol, OVERLAY_OPACITY).rgba();
\t\t\t\t\telse
\t\t\t\t\t\tradarOverlayBuffer[pos] = playerCol.rgba();
\t\t\t\t}"""
if needle not in s:
    raise SystemExit("Unsupported radar.cpp: structure color anchor not found")
s = s.replace(needle, replacement, 1)

p.write_text(s, encoding="utf-8")
print("Applied verified enemy droid/structure minimap alert patch; artifacts are not highlighted.")
