from pathlib import Path


def get_all_py(path):
    pyfiles = Path(path).glob("**/*.py")
    paths = [str(p).replace("/", ".")[:-3] for p in pyfiles]
    return {paths[i].split(".")[-1]: paths[i] for i in range(len(paths))}
