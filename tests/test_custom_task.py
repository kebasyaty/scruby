"""Test."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any
from zoneinfo import ZoneInfo

import orjson
import pytest
from pydantic import EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import CustomTask, Scruby, ScrubyModel
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


class SalaryInfo(CustomTask):
    """Custom task.

    Get information about sales salaries.

    The result should be the fields:
    `max_salary`, `min_salary`, `average_salary`, `sum_salaries`, `count_sellers`, and `salesman_list`.
    """

    def __init__(self) -> None:
        """Initializing the task."""
        self.stop_signal = False
        self.max_salary = Max()
        self.min_salary = Min()
        self.average_salary = Average()
        self.sum_salaries = Sum()
        self.salesman_list: list[Any] = []
        self.salary_info: dict[str, Any] = {}

    def accept(self, doc: Any) -> None:
        """Operation with a document."""
        self.max_salary.set(doc.salary)
        self.min_salary.set(doc.salary)
        self.average_salary.set(doc.salary)
        self.sum_salaries.set(doc.salary)
        self.salesman_list.append(doc)

    def result(self) -> Any | None:
        """Return result."""
        # Add data to result
        count_sellers = len(self.salesman_list)
        if count_sellers > 0:
            self.salary_info["max_salary"] = self.max_salary.get()
            self.salary_info["min_salary"] = self.min_salary.get()
            self.salary_info["average_salary"] = float(self.average_salary.get())
            self.salary_info["sum_salaries"] = int(self.sum_salaries.get())
            self.salary_info["count_sellers"] = count_sellers
            self.salary_info["salesman_list"] = self.salesman_list
        # Return
        return self.salary_info or None


class SalaryInfoAsJson(CustomTask):
    """Custom task.

    Get information about sales salaries in json format.

    The result should be the fields:
    `max_salary`, `min_salary`, `average_salary`, `sum_salaries`, `count_sellers`, and `salesman_list`.
    """

    def __init__(self, **kwargs) -> None:
        """Initializing the task."""
        self.stop_signal = False
        self.max_salary = Max()
        self.min_salary = Min()
        self.average_salary = Average()
        self.sum_salaries = Sum()
        self.salesman_list: list[Any] = []
        self.salary_info: dict[str, Any] = {}

    def accept(self, doc: Any) -> None:
        """Operation with a document."""
        self.max_salary.set(doc.salary)
        self.min_salary.set(doc.salary)
        self.average_salary.set(doc.salary)
        self.sum_salaries.set(doc.salary)
        self.salesman_list.append(doc)

    def result(self) -> Any | None:
        """Return result."""
        # Add data to result
        count_sellers = len(self.salesman_list)
        if count_sellers > 0:
            self.salary_info["max_salary"] = self.max_salary.get()
            self.salary_info["min_salary"] = self.min_salary.get()
            self.salary_info["average_salary"] = float(self.average_salary.get())
            self.salary_info["sum_salaries"] = int(self.sum_salaries.get())
            self.salary_info["count_sellers"] = count_sellers
            self.salary_info["salesman_list"] = [doc.model_dump() for doc in self.salesman_list]
        # Convert to JSON-string
        result_json: str = orjson.dumps(self.salesman_list).decode("utf-8")
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
    result: dict[str, Any] | None = await salesman_coll.run_custom_task(
        custom_task=SalaryInfo(),
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
    result_json: str | None = await salesman_coll.run_custom_task(
        custom_task=SalaryInfoAsJson(),
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
