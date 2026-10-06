import uuid

import pytest

from word_games.task.controller import TaskNaturalIdentifier
from word_games.view.profile import queries as _queries


@pytest.mark.parametrize(
    ("db_state", "expected"),
    [
        pytest.param({}, [], id="empty-db"),
        pytest.param(
            {
                "user": [
                    {
                        "id": 1,
                        "public_id": uuid.UUID(
                            "00000000-00000000-00000000-00000020"
                        ),
                    },
                    {
                        "public_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                    },
                ],
                "game": [
                    {
                        "public_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "creator": 1,
                    }
                ],
                "task": [
                    {
                        "game_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "assignee_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                    }
                ],
            },
            [],
            id="not-matching-entry",
        ),
        pytest.param(
            {
                "user": [
                    {
                        "id": 1,
                        "public_id": uuid.UUID(
                            "00000000-00000000-00000000-00000010"
                        ),
                    },
                    {
                        "public_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                    },
                ],
                "game": [
                    {
                        "public_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "creator": 1,
                    }
                ],
                "task": [
                    {
                        "hrid": "exhausted_kitty_1234",
                        "game_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "assignee_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                    }
                ],
            },
            [
                TaskNaturalIdentifier(
                    hrid="exhausted_kitty_1234",
                    assignee_public_id=uuid.UUID(
                        "00000000-00000000-00000000-00000000"
                    ),
                    creator_public_id=uuid.UUID(
                        "00000000-00000000-00000000-00000010"
                    ),
                )
            ],
            id="one-matching-entry",
        ),
        pytest.param(
            {
                "user": [
                    {
                        "id": 1,
                        "public_id": uuid.UUID(
                            "00000000-00000000-00000000-00000010"
                        ),
                    },
                    {
                        "public_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                    },
                ],
                "game": [
                    {
                        "public_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "creator": 1,
                    }
                ],
                "task": [
                    {
                        "hrid": "exhausted_kitty_1234",
                        "game_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "assignee_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                    },
                    {
                        "hrid": "red_lion_ddw2",
                        "game_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "assignee_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                    },
                    {
                        "hrid": "angry_bird_3523",
                        "game_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "assignee_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                    },
                ],
            },
            [
                TaskNaturalIdentifier(
                    hrid="angry_bird_3523",
                    assignee_public_id=uuid.UUID(
                        "00000000-00000000-00000000-00000000"
                    ),
                    creator_public_id=uuid.UUID(
                        "00000000-00000000-00000000-00000010"
                    ),
                ),
                TaskNaturalIdentifier(
                    hrid="exhausted_kitty_1234",
                    assignee_public_id=uuid.UUID(
                        "00000000-00000000-00000000-00000000"
                    ),
                    creator_public_id=uuid.UUID(
                        "00000000-00000000-00000000-00000010"
                    ),
                ),
                TaskNaturalIdentifier(
                    hrid="red_lion_ddw2",
                    assignee_public_id=uuid.UUID(
                        "00000000-00000000-00000000-00000000"
                    ),
                    creator_public_id=uuid.UUID(
                        "00000000-00000000-00000000-00000010"
                    ),
                ),
            ],
            id="many-matching-entry",
        ),
    ],
)
def test_select_task_natural_identifier_where_assignee_and_creator(
    db_session, task_factory, game_factory, user_factory, db_state, expected
):
    # given
    factories = {
        "task": task_factory,
        "user": user_factory,
        "game": game_factory,
    }
    for factory_name, state in db_state.items():
        factory = factories[factory_name]
        for entry in state:
            db_session.add(factory.build(**entry))
        db_session.commit()
    assignee_id = uuid.UUID("00000000-00000000-00000000-00000000")
    creator_id = uuid.UUID("00000000-00000000-00000000-00000010")

    # when
    results = (
        _queries.select_task_natural_identifier_where_assignee_and_creator(
            assignee=assignee_id,
            creator=creator_id,
        )
    )

    # then
    assert results == expected


@pytest.mark.parametrize(
    ("db_state", "expected"),
    [
        pytest.param({}, 0, id="empty-db"),
        pytest.param(
            {
                "user": [
                    {
                        "id": 1,
                        "public_id": uuid.UUID(
                            "00000000-00000000-00000000-00000010"
                        ),
                    },
                    {
                        "public_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                    },
                ],
                "game": [
                    {
                        "public_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "creator": 1,
                    }
                ],
                "task": [
                    {
                        "hrid": "exhausted_kitty_1234",
                        "game_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "assignee_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "solved": False,
                    }
                ],
            },
            1,
            id="one-matching-entry",
        ),
        pytest.param(
            {
                "user": [
                    {
                        "id": 1,
                        "public_id": uuid.UUID(
                            "00000000-00000000-00000000-00000010"
                        ),
                    },
                    {
                        "public_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                    },
                ],
                "game": [
                    {
                        "public_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "creator": 1,
                    }
                ],
                "task": [
                    {
                        "hrid": "exhausted_kitty_1234",
                        "game_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "assignee_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "solved": False,
                    },
                    {
                        "hrid": "slow_dummy_23297",
                        "game_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "assignee_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "solved": False,
                    },
                    {
                        "hrid": "black_rock_1234",
                        "game_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "assignee_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "solved": True,
                    },
                ],
            },
            3,
            id="many-matching-entry",
        ),
        pytest.param(
            {
                "user": [
                    {
                        "id": 1,
                        "public_id": uuid.UUID(
                            "00000000-00000000-00000000-00000010"
                        ),
                    },
                    {
                        "id": 2,
                        "public_id": uuid.UUID(
                            "00000000-00000000-00000000-00000020"
                        ),
                    },
                    {
                        "public_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                    },
                ],
                "game": [
                    {
                        "public_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "creator": 1,
                    },
                    {
                        "public_id": uuid.UUID(
                            "00000000-00000000-00000000-00000001"
                        ),
                        "creator": 2,
                    },
                ],
                "task": [
                    {
                        "hrid": "exhausted_kitty_1234",
                        "game_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "assignee_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "solved": False,
                    },
                    {
                        "hrid": "slow_dummy_23297",
                        "game_id": uuid.UUID(
                            "00000000-00000000-00000000-00000001"
                        ),
                        "assignee_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "solved": False,
                    },
                    {
                        "hrid": "black_rock_1234",
                        "game_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "assignee_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "solved": True,
                    },
                ],
            },
            2,
            id="many-matching-entry-different-teachers",
        ),
    ],
)
def test_count_tasks_where_assignee_id(
    db_session, task_factory, game_factory, user_factory, db_state, expected
):
    # given
    factories = {
        "task": task_factory,
        "user": user_factory,
        "game": game_factory,
    }
    for factory_name, state in db_state.items():
        factory = factories[factory_name]
        for entry in state:
            db_session.add(factory.build(**entry))
        db_session.commit()
    assignee_id = uuid.UUID("00000000-00000000-00000000-00000000")
    creator_id = uuid.UUID("00000000-00000000-00000000-00000010")

    # when
    results = _queries.count_tasks_where_assignee_and_creator(
        assignee_id, creator_id
    )

    # then
    assert results == expected


@pytest.mark.parametrize(
    ("db_state", "expected"),
    [
        pytest.param({}, 0, id="empty-db"),
        pytest.param(
            {
                "user": [
                    {
                        "id": 1,
                        "public_id": uuid.UUID(
                            "00000000-00000000-00000000-00000010"
                        ),
                    },
                    {
                        "public_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                    },
                ],
                "game": [
                    {
                        "public_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "creator": 1,
                    }
                ],
                "task": [
                    {
                        "hrid": "exhausted_kitty_1234",
                        "game_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "assignee_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "solved": True,
                    }
                ],
            },
            1,
            id="one-matching-entry",
        ),
        pytest.param(
            {
                "user": [
                    {
                        "id": 1,
                        "public_id": uuid.UUID(
                            "00000000-00000000-00000000-00000010"
                        ),
                    },
                    {
                        "public_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                    },
                ],
                "game": [
                    {
                        "public_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "creator": 1,
                    }
                ],
                "task": [
                    {
                        "hrid": "exhausted_kitty_1234",
                        "game_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "assignee_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "solved": False,
                    }
                ],
            },
            0,
            id="one-not-matching-entry",
        ),
        pytest.param(
            {
                "user": [
                    {
                        "id": 1,
                        "public_id": uuid.UUID(
                            "00000000-00000000-00000000-00000010"
                        ),
                    },
                    {
                        "public_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                    },
                ],
                "game": [
                    {
                        "public_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "creator": 1,
                    }
                ],
                "task": [
                    {
                        "hrid": "exhausted_kitty_1234",
                        "game_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "assignee_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "solved": False,
                    },
                    {
                        "hrid": "slow_dummy_23297",
                        "game_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "assignee_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "solved": False,
                    },
                    {
                        "hrid": "black_rock_1234",
                        "game_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "assignee_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "solved": True,
                    },
                ],
            },
            1,
            id="many-matching-entry",
        ),
        pytest.param(
            {
                "user": [
                    {
                        "id": 1,
                        "public_id": uuid.UUID(
                            "00000000-00000000-00000000-00000010"
                        ),
                    },
                    {
                        "id": 2,
                        "public_id": uuid.UUID(
                            "00000000-00000000-00000000-00000020"
                        ),
                    },
                    {
                        "public_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                    },
                ],
                "game": [
                    {
                        "public_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "creator": 1,
                    },
                    {
                        "public_id": uuid.UUID(
                            "00000000-00000000-00000000-00000001"
                        ),
                        "creator": 2,
                    },
                ],
                "task": [
                    {
                        "hrid": "exhausted_kitty_1234",
                        "game_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "assignee_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "solved": False,
                    },
                    {
                        "hrid": "slow_dummy_23297",
                        "game_id": uuid.UUID(
                            "00000000-00000000-00000000-00000001"
                        ),
                        "assignee_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "solved": True,
                    },
                    {
                        "hrid": "black_rock_1234",
                        "game_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "assignee_id": uuid.UUID(
                            "00000000-00000000-00000000-00000000"
                        ),
                        "solved": True,
                    },
                ],
            },
            1,
            id="many-matching-entry-different-teachers",
        ),
    ],
)
def test_count_solved_tasks_where_assignee_and_creator(
    db_session, task_factory, game_factory, user_factory, db_state, expected
):
    # given
    factories = {
        "task": task_factory,
        "user": user_factory,
        "game": game_factory,
    }
    for factory_name, state in db_state.items():
        factory = factories[factory_name]
        for entry in state:
            db_session.add(factory.build(**entry))
        db_session.commit()
    assignee_id = uuid.UUID("00000000-00000000-00000000-00000000")
    creator_id = uuid.UUID("00000000-00000000-00000000-00000010")

    # when
    results = _queries.count_solved_tasks_where_assignee_and_creator(
        assignee_id, creator_id
    )

    # then
    assert results == expected
