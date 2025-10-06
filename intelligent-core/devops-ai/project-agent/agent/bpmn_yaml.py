from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Any
import json, re, yaml, xml.etree.ElementTree as ET
from .config import get_repo_path, get_reports_dir

# Namespaces commonly used in BPMN (Camunda etc.)
BPMN_NS = {
    "bpmn": "http://www.omg.org/spec/BPMN/20100524/MODEL",
    "bpmndi": "http://www.omg.org/spec/BPMN/20100524/DI",
    "dc": "http://www.omg.org/spec/DD/20100524/DC",
    "camunda": "http://camunda.org/schema/1.0/bpmn"
}

TASK_TAGS = [
    "task","userTask","serviceTask","scriptTask","manualTask","sendTask","receiveTask","callActivity","businessRuleTask"
]

def _norm_token(s: str)->str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9\-_\.]+","-", s)
    return s[:80]

def _scan_code_hits(repo: Path, token: str)->List[str]:
    token = token.lower()
    hits = []
    for p in repo.rglob("*"):
        if p.is_dir(): 
            continue
        name = p.name.lower()
        if token and token in name and not any(x in p.as_posix() for x in [".git","node_modules",".venv","dist","build","target","bin"]):
            hits.append(p.as_posix())
            if len(hits) >= 20:
                break
    return hits

def _parse_bpmn_file(path: Path, repo: Path)->Dict[str,Any]:
    try:
        tree = ET.parse(str(path))
        root = tree.getroot()
    except Exception:
        return {"file": path.as_posix(), "processes": []}
    procs = []
    # iterate processes
    for proc in root.findall(".//bpmn:process", BPMN_NS):
        p_id = proc.attrib.get("id","")
        p_name = proc.attrib.get("name", p_id)
        tasks = []
        for tag in TASK_TAGS:
            for t in proc.findall(f".//bpmn:{tag}", BPMN_NS):
                tid = t.attrib.get("id","")
                tname = t.attrib.get("name", tid)
                impl = t.attrib.get("{%s}class" % BPMN_NS["camunda"]) if "camunda" in BPMN_NS else None
                candidate = impl or tname or tid
                token = _norm_token(candidate)
                code_refs = _scan_code_hits(repo, token) if token else []
                tasks.append({
                    "id": tid, "name": tname, "type": tag,
                    "camundaClass": impl, "token": token, "code_refs": code_refs
                })
        procs.append({
            "id": p_id, "name": p_name,
            "tasks": tasks,
            "file": path.as_posix()
        })
    return {"file": path.as_posix(), "processes": procs}

def _parse_yaml_json_file(path: Path, repo: Path)->Dict[str,Any]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return {"file": path.as_posix(), "artifacts": []}
    items = []
    data = None
    try:
        if path.suffix.lower() in (".yaml",".yml"):
            data = yaml.safe_load(text)
        elif path.suffix.lower() == ".json":
            import json as _json
            data = _json.loads(text)
    except Exception:
        data = None
    # heuristic: look for keys that suggest workflows/policies/services
    keys_of_interest = {"workflow","pipelines","pipeline","service","services","policy","policies","bpm","bpmn","tasks"}
    def walk(node, prefix=""):
        if isinstance(node, dict):
            for k,v in node.items():
                kstr = str(k).lower()
                if kstr in keys_of_interest:
                    token = _norm_token(kstr)
                    code_refs = _scan_code_hits(repo, token)
                    items.append({"key": kstr, "path": prefix + "/" + str(k), "code_refs": code_refs})
                walk(v, prefix + "/" + str(k))
        elif isinstance(node, list):
            for i,v in enumerate(node):
                walk(v, prefix + f"/[{i}]")
        else:
            pass
    if data is not None:
        walk(data, "")
    return {"file": path.as_posix(), "artifacts": items}

def build_process_map():
    repo = get_repo_path()
    reports = get_reports_dir()
    result: Dict[str,Any] = {"bpmn": [], "yaml_json": []}

    # BPMN
    for p in repo.rglob("*.bpmn"):
        if ".git" in p.as_posix():
            continue
        result["bpmn"].append(_parse_bpmn_file(p, repo))

    # YAML/JSON
    for p in repo.rglob("*"):
        if p.suffix.lower() in (".yaml",".yml",".json"):
            if any(seg in p.as_posix() for seg in [".git","node_modules",".venv","dist","build","target","bin"]):
                continue
            result["yaml_json"].append(_parse_yaml_json_file(p, repo))

    (reports/"process_map.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result
