import os
import logging
import pytest
from chempiler.tools.graph import ChempilerGraph
from chempiler.tools.errors import ChempilerError
import ChemputerAPI

HERE = os.path.dirname(os.path.abspath(__file__))
GRAPH_FILE = os.path.join(HERE, "graph_files", "duplicate_node_names.json")

logger = logging.getLogger("test_graph")

def test_duplicate_node_names():
    with pytest.raises(ChempilerError):
        ChempilerGraph(
            GRAPH_FILE, logger, [ChemputerAPI], simulation=True)
