"""A configuration is independent of any Fleet installation."""
from pathlib import Path
from operation_contracts.common import ContractError, fields, identifier, load
from operation_contracts.projects import Projects
from operation_contracts.journal import Journal
from .catalog import Catalog
from .engine import Operations


def configured(path):
    document = load(path)
    fields(document,("version","principal","projects_file","state_dir","surface","session"),
           ("actions","mcp_endpoints"))
    if type(document["version"]) is not int or document["version"] != 1:
        raise ContractError("A configuration version must be 1")
    identifier(document["principal"])
    identifier(document["session"])
    base = Path(path).expanduser().resolve().parent
    for key in ("projects_file", "state_dir"):
        item = Path(document[key]).expanduser()
        document[key] = str(item if item.is_absolute() else base / item)
    for configs in document.get("mcp_endpoints", {}).values():
        for endpoint in configs if isinstance(configs, list) else [configs]:
            if "headers_file" in endpoint:
                item = Path(endpoint["headers_file"]).expanduser()
                endpoint["headers_file"] = str(item if item.is_absolute() else base / item)
    projects = Projects.from_file(document["projects_file"])
    journal = Journal(Path(document["state_dir"]).expanduser() / "operations.sqlite3")
    engine = Operations(projects,journal,document["principal"],surface=document["surface"],
                        session=document["session"],catalog=Catalog(document.get("actions")))
    return engine, document
