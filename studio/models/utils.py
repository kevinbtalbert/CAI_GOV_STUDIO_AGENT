# No top level studio.db imports allowed to support wokrflow model deployment

from typing import Tuple, Annotated, Union
from pydantic import Field


def get_studio_default_model_id(
    dao=None,
    preexisting_db_session=None,
) -> Tuple[
    Annotated[bool, Field(description="Is default set")], Union[Annotated[str, Field(description="Model ID")], None]
]:
    """
    Get the default model ID for the studio.
    """

    from studio.db import DbSession, model as db_model

    session: DbSession = preexisting_db_session or dao.get_session()
    model = session.query(db_model.Model).filter_by(is_studio_default=True).one_or_none()
    if not model:
        if not preexisting_db_session:
            session.close()
        return False, None

    if not preexisting_db_session:
        session.close()
    return True, model.model_id
