"""Test."""

from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from datetime import datetime
from threading import Event
from typing import Annotated, Any
from zoneinfo import ZoneInfo

import orjson
import pytest
from pydantic import EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import Scruby, ScrubyModel
from scruby.aggregation import Average, Max, Min, Sum

pytestmark = pytest.mark.asyncio(loop_scope="module")

# Delete DB.
# Hint: If the previous test failed and the database remains.
Scruby.napalm()


class Salesman(ScrubyModel):
    """Salesman model."""

    username: str
    first_name: str
    last_name: str
    birthday: datetime
    email: EmailStr
    phone: Annotated[PhoneNumber, PhoneNumberValidator(number_format="E164"), Field(strict=False)]
    salary: int
    # key is always at bottom
    key: Annotated[
        str,
        Field(
            frozen=True,
            default_factory=lambda data: data["phone"],
        ),
    ]


def salary_info(
    search_task_fn: Callable,
    filter_fn: Callable,
    hash_reduce_left: int,
    branch_numbers: range,
    class_model: Any,
    max_workers: int | None,
    stop_signal: Event,
) -> dict[str, Any] | None:
    """Custom task.

    Get information about sales salaries.

    The result should be the fields:
    `max_salary`, `min_salary`, `average_salary`, `sum_salaries`, `count_sellers`, and `salesman_list`.
    """
    max_salary = Max()
    min_salary = Min()
    average_salary = Average()
    sum_salaries = Sum()
    salesman_list: list[Any] = []
    result: dict[str, Any] = {}
    # Run quantum loop
    with ThreadPoolExecutor(max_workers) as executor:
        futures: list[Future] = [
            executor.submit(
                search_task_fn,
                filter_fn,
                hash_reduce_left,
                branch_number,
                class_model,
                stop_signal,
            )
            for branch_number in branch_numbers
        ]
        for future in as_completed(futures):
            docs = future.result()
            if docs is not None:
                for doc in docs:
                    max_salary.set(doc.salary)
                    min_salary.set(doc.salary)
                    average_salary.set(doc.salary)
                    sum_salaries.set(doc.salary)
                    salesman_list.append(doc)
    # Add data to result
    count_sellers = len(salesman_list)
    if count_sellers > 0:
        result["max_salary"] = max_salary.get()
        result["min_salary"] = min_salary.get()
        result["average_salary"] = float(average_salary.get())
        result["sum_salaries"] = int(sum_salaries.get())
        result["count_sellers"] = count_sellers
        result["salesman_list"] = salesman_list
    # Return
    return result or None


def salary_info_as_json(
    search_task_fn: Callable,
    filter_fn: Callable,
    hash_reduce_left: int,
    branch_numbers: range,
    class_model: Any,
    max_workers: int | None,
    stop_signal: Event,
) -> str | None:
    """Custom task.

    Get information about sales salaries in json format.

    The result should be the fields:
    `max_salary`, `min_salary`, `average_salary`, `sum_salaries`, `count_sellers`, and `salesman_list`.
    """
    max_salary = Max()
    min_salary = Min()
    average_salary = Average()
    sum_salaries = Sum()
    salesman_list: list[Any] = []
    result: dict[str, Any] = {}
    # Run quantum loop
    with ThreadPoolExecutor(max_workers) as executor:
        futures: list[Future] = [
            executor.submit(
                search_task_fn,
                filter_fn,
                hash_reduce_left,
                branch_number,
                class_model,
                stop_signal,
            )
            for branch_number in branch_numbers
        ]
        for future in as_completed(futures):
            docs = future.result()
            if docs is not None:
                for doc in docs:
                    max_salary.set(doc.salary)
                    min_salary.set(doc.salary)
                    average_salary.set(doc.salary)
                    sum_salaries.set(doc.salary)
                    salesman_list.append(doc)
    # Add data to result
    count_sellers = len(salesman_list)
    if count_sellers > 0:
        result["max_salary"] = max_salary.get()
        result["min_salary"] = min_salary.get()
        result["average_salary"] = float(average_salary.get())
        result["sum_salaries"] = int(sum_salaries.get())
        result["count_sellers"] = count_sellers
        result["salesman_list"] = [doc.model_dump() for doc in salesman_list]
    # Convert to JSON-string
    result_json: str = orjson.dumps(result).decode("utf-8")
    # Return
    return result_json if count_sellers > 0 else None


async def test_salary_info() -> None:
    """Test a salary_info custom task."""
    # Activate database.
    Scruby.run()

    # Get collection `Salesman`
    salesman_coll = Scruby(Salesman)

    # Create sellers
    for num in range(1, 10):
        salesman = Salesman(
            username=f"salesman_{num}",
            first_name="John",
            last_name="Smith",
            birthday=datetime(1970, 1, num, tzinfo=ZoneInfo("UTC")),
            email=f"John_Smith_{num}@gmail.com",
            phone=f"+44798612345{num}",
            salary=num,
        )
        await salesman_coll.add_doc(salesman)

    # Get salary information for sellers named John
    result: dict[str, Any] | None = salesman_coll.run_custom_task(
        custom_task_fn=salary_info,
        filter_fn=lambda doc: doc.first_name == "John",
    )

    # Check
    assert result is not None
    assert result["max_salary"] == 9
    assert result["min_salary"] == 1
    assert result["average_salary"] == pytest.approx(5.0)
    assert result["sum_salaries"] == 45
    assert result["count_sellers"] == 9
    assert isinstance(result["salesman_list"][0], Salesman)
    #
    # Delete DB.
    Scruby.napalm()


async def test_salary_info_as_json() -> None:
    """Test a salary_info_as_json custom task."""
    # Activate database.
    Scruby.run()

    # Get collection `Salesman`
    salesman_coll = Scruby(Salesman)

    # Create sellers
    for num in range(1, 10):
        salesman = Salesman(
            username=f"salesman_{num}",
            first_name="John",
            last_name="Smith",
            birthday=datetime(1970, 1, num, tzinfo=ZoneInfo("UTC")),
            email=f"John_Smith_{num}@gmail.com",
            phone=f"+44798612345{num}",
            salary=num,
        )
        await salesman_coll.add_doc(salesman)

    # Get salary information for sellers named John
    result_json: str | None = salesman_coll.run_custom_task(
        custom_task_fn=salary_info_as_json,
        filter_fn=lambda doc: doc.first_name == "John",
    )

    # Check
    assert result_json is not None
    assert isinstance(result_json, str)
    #
    result = orjson.loads(result_json)
    #
    assert result["max_salary"] == 9
    assert result["min_salary"] == 1
    assert result["average_salary"] == pytest.approx(5.0)
    assert result["sum_salaries"] == 45
    assert result["count_sellers"] == 9
    assert isinstance(result["salesman_list"][0], dict)
    #
    # Delete DB.
    Scruby.napalm()
