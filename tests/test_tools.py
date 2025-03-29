import pytest
from unittest.mock import patch, MagicMock

from studio.api import *
from studio.db.dao import AgentStudioDao
from studio.db import model as db_model
from studio.tools.tool_template import *
from studio.tools.utils import (
    extract_user_params_from_code,
    extract_tool_class_name
)
import json



