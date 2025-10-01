import os, re, socket, yaml, pathlib, json, time
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple

ROOT = pathlib.Path(__file__).resolve().parents[2]
K8S_DIR = ROOT / "k8s" / "manifests"
DC_YML = ROOT / "docker-compose.yml"
DOCS = ROOT / "docs" / "graphs"
DOCS.mkdir(parents=True, exist_ok=True)

@dataclass
class Svc:
    name: str
    kind: str
    image: Optional[str] = None
    ports: List[int] = None
    env: Dict[str, str] = None

@dataclass
class Edge:
    frm: str
    to: str
    reason: str

def _read_yaml_files() -> List[dict]:
    out = []
    if K8S_DIR.exists():
        for p in sorted(K8S_DIR.rglob("*.y*ml")):
            try:
                out.append(yaml.safe_load(p.read_text()))
            except Exception:
                pass
    if DC_YML.exists():
        try:
            out.append(yaml.safe_load(DC_YML.read_text()))
        except Exception:
            pass
    return out

def _k8s_ports(obj) -> List[int]:
    ports = []
    c = (obj or {}).get("spec", {}).get("template", {}).get("spec", {}).get("containers", [])
    for cont in c:
        for prt in cont.get("ports", []) or []:
            val = prt.get("containerPort") or prt.get("hostPort")
            if isinstance(val, int):
                ports.append(val)
    return sorted(set(ports))

def _k8s_env(obj) -> Dict[str, str]:
    env = {}
    c = (obj or {}).get("spec", {}).get("template", {}).get("spec", {}).get("containers", [])
    for cont in c:
        for e in cont.get("env", []) or []:
            k, v = e.get("name"), e.get("value")
            if k and v is not None:
                env[k] = str(v)
    return env

def _compose_services(obj) -> Dict[str, Svc]:
    out = {}
    svcs = (obj or {}).get("services", {}) or {}
    for name, spec in svcs.items():
        img = spec.get("image")
        ports = []
        for p in spec.get("ports", []) or []:
            # "8080:80" or "127.0.0.1:8080:80"
            left = str(p).split(":")[0]
            try:
                ports.append(int(left.split("/") [0].split(":")[-1]))
            except Exception:
                pass
        env = {}
        for e in spec.get("environment", []) or []:
            if isinstance(e, str) and "=" in e:
                k, v = e.split("=", 1); env[k] = v
            elif isinstance(e, dict):
                for k, v in e.items(): env[k] = str(v)
        out[name] = Svc(name=name, kind="compose", image=img, ports=sorted(set(ports)), env=env)
    return out

def load_graph() -> Tuple[Dict[str, Svc], List[Edge]]:
    services: Dict[str, Svc] = {}
    edges: List[Edge] = []
    yamls = _read_yaml_files()
    for obj in yamls:
        if not obj: continue
        # docker-compose
        if "services" in obj:
            services.update(_compose_services(obj))
            continue
        # k8s kinds
        kind = obj.get("kind")
        meta = (obj or {}).get("metadata", {}) or {}
        name = meta.get("name")
        if kind in {"Deployment","StatefulSet","DaemonSet"} and name:
            img = None
            cs = (obj or {}).get("spec", {}).get("template", {}).get("spec", {}).get("containers", [])
            if cs:
                img = cs[0].get("image")
            services[name] = Svc(
                name=name, kind=kind.lower(), image=img,
                ports=_k8s_ports(obj), env=_k8s_env(obj)
            )

    # infer edges via env values that look like hostnames of other services or URLs
    svc_keys = set(services.keys())
    hostlike = re.compile(r"^(?:https?://)?([a-zA-Z0-9\-_\.]+)")
    for a in services.values():
        for _, v in (a.env or {}).items():
            m = hostlike.match(str(v).strip())
            if not m: continue
            host = m.group(1).split(":")[0]
            if host in svc_keys and host != a.name:
                edges.append(Edge(frm=a.name, to=host, reason="env_ref"))
    return services, edges

def port_conflicts(services: Dict[str, Svc]) -> List[Dict[str, str]]:
    seen = {}
    issues = []
    for s in services.values():
        for p in (s.ports or []):
            k = f"{p}"
            if k in seen:
                issues.append({"port": p, "services": [seen[k], s.name], "reason":"port_collision"})
            else:
                seen[k] = s.name
    return issues

def local_port_bound(p: int) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.2)
    try:
        return sock.connect_ex(("127.0.0.1", p)) == 0
    finally:
        sock.close()

def write_outputs(services: Dict[str, Svc], edges: List[Edge]) -> None:
    # JSON
    (DOCS / "service_graph.json").write_text(
        json.dumps({
            "generated": int(time.time()),
            "services": [asdict(s) for s in services.values()],
            "edges": [asdict(e) for e in edges],
        }, indent=2),
        encoding="utf-8"
    )
    # Mermaid
    lines = ["flowchart LR"]
    for s in services.values():
        label = f"{s.name}\\n({s.kind})"
        lines.append(f'  {s.name}["{label}"]')
    for e in edges:
        lines.append(f"  {e.frm} -->|{e.reason}| {e.to}")
    (DOCS / "service_graph.mmd").write_text("\n".join(lines)+"\n", encoding="utf-8")

    # Heal plan for port conflicts
    plan = {"generated": int(time.time()), "items": []}
    conflicts = port_conflicts(services)
    for c in conflicts:
        p = c["port"]; a, b = c["services"]
        suggestion = {
            "type":"change_port",
            "port": p,
            "services": [a,b],
            "suggestion": f"Remap one service hostPort/containerPort for {p}. Example: map {p} -> {p+10} for {b}."
        }
        plan["items"].append(suggestion)
    # Check if any declared ports already bound locally
    for s in services.values():
        for p in (s.ports or []):
            if local_port_bound(p):
                plan["items"].append({
                    "type":"port_bound_locally",
                    "service": s.name,
                    "port": p,
                    "suggestion": f"Port {p} already bound on localhost. Use alternate mapping or stop local process."
                })
    (DOCS / "heal_plan_service_ports.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")

def main():
    svcs, edges = load_graph()
    write_outputs(svcs, edges)
    print(f"Wrote docs/graphs/service_graph.mmd and .json; heal plan generated.")

if __name__ == "__main__":
    main()