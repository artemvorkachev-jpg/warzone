#!/usr/bin/env python3
"""Apply the minimap alert change to the pinned Warzone 2100 4.7.0 source."""
from pathlib import Path

p = Path("src/radar.cpp")
s = p.read_text(encoding="utf-8")
if "MINIMAP_ENEMY_ALERTS_PATCH" in s:
    print("Minimap alert patch already applied.")
    raise SystemExit(0)

needle = '#include "objects.h"\n'
if needle not in s:
    raise SystemExit("Unsupported radar.cpp: objects.h include anchor not found")
s = s.replace(needle, needle + '#include "feature.h"\n', 1)

needle = """\tbool blinkState = (gameTime - lastBlink) / BLINK_HALF_INTERVAL;

\t/* Show droids on map - go through all players */"""
replacement = """\tbool blinkState = (gameTime - lastBlink) / BLINK_HALF_INTERVAL;

\t// MINIMAP_ENEMY_ALERTS_PATCH: steady yellow contacts near mission end.
\tint hostileObjectsRemaining = 0;
\tfor (UBYTE player = 0; player < MAX_PLAYERS; ++player)
\t{
\t\tif (player == selectedPlayer || aiCheckAlliances(selectedPlayer, player))
\t\t{
\t\t\tcontinue;
\t\t}
\t\tfor (const DROID* droid : apsDroidLists[player]) { (void)droid; ++hostileObjectsRemaining; }
\t\tfor (const STRUCTURE* structure : apsStructLists[player]) { (void)structure; ++hostileObjectsRemaining; }
\t}
\tfor (const FEATURE* feature : GlobalFeatureContainer())
\t{
\t\tif (feature && feature->psStats && feature->psStats->subType == FEAT_GEN_ARTE)
\t\t{
\t\t\t++hostileObjectsRemaining;
\t\t}
\t}
\tconst bool lowMissionTime = mission.time >= 0
\t\t&& gameTime >= mission.startTime
\t\t&& mission.time - static_cast<SDWORD>(gameTime - mission.startTime) < 5 * 60 * GAME_TICKS_PER_SEC;
\tconst bool minimapAlert = lowMissionTime || hostileObjectsRemaining < 10;

\t/* Show droids on map - go through all players */"""
if needle not in s:
    raise SystemExit("Unsupported radar.cpp: DrawRadarObjects start anchor not found")
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

# Draw artifact locations as yellow dots while the alert is active.
needle = """\tif (gameTime - lastBlink >= BLINK_INTERVAL)
\t\tlastBlink = gameTime;
}"""
replacement = """\tif (minimapAlert)
\t{
\t\tfor (const FEATURE* feature : GlobalFeatureContainer())
\t\t{
\t\t\tif (!feature || !feature->psStats || feature->psStats->subType != FEAT_GEN_ARTE)
\t\t\t{
\t\t\t\tcontinue;
\t\t\t}
\t\t\tif (feature->pos.x < world_coord(scrollMinX) || feature->pos.y < world_coord(scrollMinY)
\t\t\t    || feature->pos.x >= world_coord(scrollMaxX) || feature->pos.y >= world_coord(scrollMaxY))
\t\t\t{
\t\t\t\tcontinue;
\t\t\t}
\t\t\tconst int x = feature->pos.x / TILE_UNITS;
\t\t\tconst int y = feature->pos.y / TILE_UNITS;
\t\t\tconst size_t pos = (x - scrollMinX) + (y - scrollMinY) * radarTexWidth;
\t\t\tASSERT(pos * sizeof(*radarOverlayBuffer) < radarBufferSize, "Buffer overrun");
\t\t\tradarOverlayBuffer[pos] = WZCOL_YELLOW.rgba();
\t\t}
\t}
\tif (gameTime - lastBlink >= BLINK_INTERVAL)
\t\tlastBlink = gameTime;
}"""
if needle not in s:
    raise SystemExit("Unsupported radar.cpp: end-of-function anchor not found")
s = s.replace(needle, replacement, 1)
p.write_text(s, encoding="utf-8")
print("Applied minimap enemy alert patch to src/radar.cpp")
