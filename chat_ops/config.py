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
    projects = Projects.from_file(document["projects_file"])
    journal = Journal(Path(document["state_dir"]).expanduser() / "operations.sqlite3")
    engine = Operations(projects,journal,document["principal"],surface=document["surface"],
                        session=document["session"],catalog=Catalog(document.get("actions")))
    return engine, document
