"""Run archived Blender scripts using repository-local input/output paths."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
TASKS = {
    ("robot", "build"): "cases/robot/release/scripts/droplet_shell_v29.py",
    ("robot", "render"): "cases/robot/release/scripts/render_v29.py",
    ("sheep", "build"): "cases/sheep/release/scripts/sheep_v11.py",
}


def prepare(case, action):
    """Resolve inputs and adapt paths; no Blender import or model mutation here."""
    source_path = ROOT / TASKS[(case, action)]
    output = ROOT / "build" / case
    baseline = ROOT / "cases/robot/droplet_shell_model_BASELINE.blend"
    if case == "robot" and action == "build" and not baseline.is_file():
        raise FileNotFoundError(baseline)
    if case == "robot" and action == "render":
        model = output / "droplet_shell_model_v29_detail.blend"
        if not model.is_file():
            raise FileNotFoundError(f"Run robot build first: {model}")
    source = source_path.read_text(encoding="utf-8")
    source = source.replace(
        "/home/oa312/workspace/droplet_shell_model_BASELINE.blend",
        baseline.as_posix(),
    )
    old_root = "/home/oa312/workspace"
    if case == "sheep":
        old_root += "/sheep_3d"
    source = source.replace(old_root, output.as_posix())
    return source_path, output, compile(source, str(source_path), "exec")


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    if len(args) != 2 or tuple(args) not in TASKS:
        raise SystemExit("Usage: blender -b -P tools/run_case.py -- {robot build|robot render|sheep build}")
    source_path, output, code = prepare(*args)
    output.mkdir(parents=True, exist_ok=True)
    print(f"Running {source_path.name}; output: {output}", flush=True)
    exec(code, {"__name__": "__main__", "__file__": str(source_path)})


if __name__ == "__main__":
    main()
