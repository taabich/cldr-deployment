# filter_plugins/cm_updates.py
# Custom filters to build Cloudera Manager config update payloads

import re

def cm_role_updates(cluster_update_config):
    """
    Build (service, roleType, settings) for all non-SERVICEWIDE role configs.
    Input: dict cluster_update_config
    Return: list[ {service, roleType, settings} ]
    """
    out = []
    cfg = cluster_update_config or {}
    if not isinstance(cfg, dict):
        return out

    for svc, per_svc in cfg.items():
        if svc == "mgmt_configs" or not isinstance(per_svc, dict):
            continue
        for role_type, settings in per_svc.items():
            if role_type in ("SERVICEWIDE", "mgmt_configs"):
                continue
            if isinstance(settings, dict) and settings:
                out.append({
                    "service": svc,
                    "roleType": role_type,
                    "settings": settings
                })
    return out


def _pick_rcg(matches):
    """Prefer *-BASE; else first match."""
    if not matches:
        return None
    base = [r for r in matches if re.search(r"-BASE$", r.get("name", ""))]
    return base[0] if base else matches[0]


def cm_resolve_role_updates(role_updates_list, rcg_lookup):
    """
    Resolve Role Config Group name for each role update.
    rcg_lookup: {service: [{"name": "...","roleType": "..."}, ...]}
    Return: list[{service, roleType, rcgName, settings, guessed?}]
    """
    out = []
    rul = role_updates_list or []
    lookup = rcg_lookup or {}

    for u in rul:
        svc = u.get("service")
        rtype = u.get("roleType")
        rcgs = lookup.get(svc, []) or []
        matches = [r for r in rcgs if r.get("roleType") == rtype]
        pick = _pick_rcg(matches)

        if pick:
            out.append({
                "service": svc,
                "roleType": rtype,
                "rcgName": pick.get("name"),
                "settings": u.get("settings", {})
            })
        else:
            guess = f"{(svc or '').lower()}-{rtype}-BASE"
            out.append({
                "service": svc,
                "roleType": rtype,
                "rcgName": guess,
                "settings": u.get("settings", {}),
                "guessed": True
            })
    return out


def cm_mgmt_updates(mgmt_cfgs, mgmt_rcgs_items):
    """
    Build mgmt role updates from mgmt_configs and discovered mgmt RCGs.
    mgmt_rcgs_items: list[{"name":"...", "roleType":"..."}]
    Return: list[{rcgName, settings, guessed?}]
    """
    out = []
    mg = mgmt_cfgs or {}
    rcgs = mgmt_rcgs_items or []

    for role_type, settings in mg.items():
        matches = [r for r in rcgs if r.get("roleType") == role_type]
        pick = _pick_rcg(matches)
        if pick:
            out.append({
                "rcgName": pick.get("name"),
                "settings": settings
            })
        else:
            guess = f"mgmt-{role_type}-BASE"
            out.append({
                "rcgName": guess,
                "settings": settings,
                "guessed": True
            })
    return out


class FilterModule(object):
    def filters(self):
        return {
            "cm_role_updates": cm_role_updates,
            "cm_resolve_role_updates": cm_resolve_role_updates,
            "cm_mgmt_updates": cm_mgmt_updates,
        }