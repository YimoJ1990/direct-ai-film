#!/usr/bin/env python3
"""Validate film project timing and reference/role integrity. No network or mutation."""
import argparse
import json
import math
import sys
from pathlib import Path

ASSET_TYPES = {'character', 'clothing', 'scene', 'prop', 'product', 'continuity_frame', 'style'}
STAGES = {'planned', 'plan_approved', 'images_generated', 'assets_approved', 'prompts_ready'}
STATUSES = {'existing', 'missing', 'candidate', 'approved', 'generated', 'failed'}

def validate(data):
    errors, warnings = [], []
    def need(condition, message):
        if not condition:
            errors.append(message)
    def number(value):
        return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
    if not isinstance(data, dict):
        return ['project must be an object'], []
    for key in ('project_id', 'version'):
        need(isinstance(data.get(key), str) and bool(data.get(key)), f'{key}: required string')
    need(data.get('mode') in {'review', 'direct', 'prompts_only'}, 'invalid mode')
    need(data.get('stage') in STAGES, 'invalid stage')
    source = data.get('source')
    need(isinstance(source, dict) and bool(source.get('version')), 'source.version: required')
    assets = data.get('assets', [])
    segments = data.get('segments', [])
    approvals = data.get('approvals', [])
    for key, value in [('assets', assets), ('segments', segments), ('approvals', approvals)]:
        need(isinstance(value, list), f'{key}: must be array')
    if not all(isinstance(v, list) for v in (assets, segments, approvals)):
        return errors, warnings
    by_id = {}
    for a in assets:
        if not isinstance(a, dict):
            errors.append('asset must be object'); continue
        aid = a.get('id')
        need(isinstance(aid, str) and bool(aid), 'asset.id: required string')
        if not isinstance(aid, str):
            continue
        need(aid not in by_id, f'duplicate asset {aid}')
        by_id[aid] = a
        need(a.get('type') in ASSET_TYPES, f'{aid}: invalid type')
        need(a.get('status') in STATUSES, f'{aid}: invalid status')
        need(bool(a.get('name')), f'{aid}: missing name')
        if a.get('status') in {'generated', 'candidate', 'approved'}:
            need(bool(a.get('path') or a.get('library_file_id')), f'{aid}: missing generated artifact identity')
    for a in assets:
        if isinstance(a, dict) and a.get('owner'):
            need(by_id.get(a['owner'], {}).get('type') == 'character', f"{a.get('id')}: owner not character")
    for a in approvals:
        if not isinstance(a, dict):
            errors.append('approval must be object'); continue
        need(a.get('scope') in {'plan', 'images', 'assets', 'prompts'}, 'invalid approval scope')
        need(bool(a.get('version') and a.get('evidence')), 'approval lacks version/evidence')
    if data.get('mode') == 'review' and data.get('stage') in STAGES - {'planned'}:
        need(any(a.get('scope') == 'plan' and a.get('version') == data.get('version') and a.get('evidence')
                 for a in approvals if isinstance(a, dict)), 'review stage lacks current plan approval')
    need(bool(segments), 'segments empty')
    seen_segments, seen_shots = set(), set()
    previous_global_end = None
    for seg in segments:
        if not isinstance(seg, dict):
            errors.append('segment must be object'); continue
        sid = seg.get('id')
        if not isinstance(sid, str) or not sid:
            errors.append('segment.id required'); continue
        need(sid not in seen_segments, f'duplicate segment {sid}'); seen_segments.add(sid)
        need(bool(seg.get('title') and seg.get('scene_id')), f'{sid}: title/scene_id missing')
        dur, global_start = seg.get('duration'), seg.get('global_start')
        if not number(dur) or dur <= 0 or not number(global_start) or global_start < 0:
            errors.append(f'{sid}: invalid duration/global_start'); continue
        if previous_global_end is not None:
            need(global_start >= previous_global_end - 1e-6, f'{sid}: global overlap')
            if not data.get('allow_global_gaps'):
                need(abs(global_start - previous_global_end) < 1e-6, f'{sid}: global gap')
        previous_global_end = global_start + dur
        refs = seg.get('references', [])
        need(isinstance(refs, list), f'{sid}: references must be array')
        if not isinstance(refs, list): refs = []
        indices = []
        for r in refs:
            if not isinstance(r, dict):
                errors.append(f'{sid}: reference must be object'); continue
            indices.append(r.get('index'))
            need(r.get('asset_id') in by_id, f'{sid}: unknown reference asset')
            need(bool(r.get('role')), f'{sid}: reference role missing')
        need(indices == list(range(1, len(indices) + 1)), f'{sid}: reference numbering not contiguous')
        if seg.get('first_frame_asset_id'):
            need(by_id.get(seg['first_frame_asset_id'], {}).get('type') == 'continuity_frame', f'{sid}: invalid first frame asset')
        shots = seg.get('shots', [])
        need(isinstance(shots, list) and bool(shots), f'{sid}: shots missing')
        if not isinstance(shots, list): continue
        cursor = 0.0
        for shot in shots:
            if not isinstance(shot, dict):
                errors.append(f'{sid}: shot must be object'); continue
            shid = shot.get('id')
            if not isinstance(shid, str) or not shid:
                errors.append(f'{sid}: shot.id required'); continue
            need(shid not in seen_shots, f'duplicate shot {shid}'); seen_shots.add(shid)
            start, end = shot.get('start'), shot.get('end')
            if not number(start) or not number(end) or end <= start:
                errors.append(f'{shid}: invalid time'); continue
            need(abs(start - cursor) < 1e-6, f'{shid}: local gap/overlap')
            cursor = end
            for key in ('action', 'camera', 'end_state'):
                need(bool(shot.get(key)), f'{shid}: {key} missing')
            chars = shot.get('characters', [])
            need(isinstance(chars, list), f'{shid}: characters must be array')
            if not isinstance(chars, list): chars = []
            for char in chars:
                need(by_id.get(char, {}).get('type') == 'character', f'{shid}: invalid character {char}')
            lines = shot.get('dialogue', [])
            need(isinstance(lines, list), f'{shid}: dialogue must be array')
            if not isinstance(lines, list): lines = []
            words = 0
            for line in lines:
                if not isinstance(line, dict):
                    errors.append(f'{shid}: dialogue must be object'); continue
                speaker = line.get('speaker')
                need(by_id.get(speaker, {}).get('type') == 'character', f'{shid}: invalid speaker')
                need(speaker in chars or line.get('offscreen') is True, f'{shid}: speaker absent without offscreen flag')
                need(isinstance(line.get('text'), str) and bool(line.get('text')), f'{shid}: dialogue text missing')
                words += len(str(line.get('text', '')).split())
            if words / (end - start) * 60 > 170:
                warnings.append(f'{shid}: dialogue >170 tokens/minute; check actual language and recording')
        need(abs(cursor - dur) < 1e-6, f'{sid}: shots do not total duration')
    return errors, warnings

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.project.read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        print(f'INPUT ERROR: {exc}', file=sys.stderr); return 2
    errors, warnings = validate(data)
    for message in errors: print('ERROR:', message)
    for message in warnings: print('WARN:', message)
    print(f'{len(errors)} error(s), {len(warnings)} warning(s)')
    return 1 if errors else 0

if __name__ == '__main__':
    sys.exit(main())
