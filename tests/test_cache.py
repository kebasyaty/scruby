"""Testing Cache."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from zoneinfo import ZoneInfo

import pytest
from pydantic import EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

from scruby import ReturnType, Scruby, ScrubyConfig, ScrubyModel
from scruby.cache import DocCache

pytestmark = pytest.mark.asyncio(loop_scope="module")

# Delete DB.
Scruby.napalm()
ScrubyConfig.db_root = "TestScrubyDB"
Scruby.napalm()


class User(ScrubyModel):
    """User model."""

    first_name: str = Field(strict=True)
    last_name: str = Field(strict=True)
    birthday: datetime = Field(strict=True)
    email: EmailStr = Field(strict=True)
    phone: Annotated[PhoneNumber, PhoneNumberValidator(number_format="E164")] = Field(frozen=True)
    # key is always at bottom
    key: str = Field(
        strict=True,
        frozen=True,
        default_factory=lambda data: data["phone"],
    )


class Phone(ScrubyModel):
    """Phone model."""

    brand: str = Field(strict=True, frozen=True)
    model: str = Field(strict=True, frozen=True)
    screen_diagonal: float = Field(strict=True)
    matrix_type: str = Field(strict=True)
    # key is always at bottom
    key: str = Field(
        strict=True,
        frozen=True,
        default_factory=lambda data: f"{data['brand']}:{data['model']}",
    )


class Car(ScrubyModel):
    """Car model."""

    brand: str = Field(strict=True, frozen=True)
    model: str = Field(strict=True, frozen=True)
    year: int = Field(strict=True)
    power_reserve: int = Field(strict=True)
    # key is always at bottom
    key: str = Field(
        strict=True,
        frozen=True,
        default_factory=lambda data: f"{data['brand']}:{data['model']}",
    )


# Activate database.
Scruby.run(db_root="TestScrubyDB")


async def test_create_db() -> None:
    """Create a test database."""
    # Create users
    user_coll = await Scruby.collection(User)
    for num in range(9):
        user = User(
            first_name="John",
            last_name="Smith",
            birthday=datetime(1970, 1, 1, tzinfo=ZoneInfo("UTC")),
            email="John_Smith@gmail.com",
            phone=f"+44798612345{num}",
        )
        # Add user to collection.
        await user_coll.add_doc(user)

    # Create phones
    phone_coll = await Scruby.collection(Phone)
    for num in range(9):
        phone = Phone(
            brand="Samsung",
            model=f"Galaxy A26 {num}",
            screen_diagonal=6.7,
            matrix_type="Super AMOLED",
        )
        # Add phone to collection.
        await phone_coll.add_doc(phone)

    # Create cars
    car_coll = await Scruby.collection(Car)
    for num in range(9):
        car = Car(
            brand="Mazda",
            model=f"EZ-6 {num}",
            year=2025,
            power_reserve=600,
        )
        # Add car to collection
        await car_coll.add_doc(car)


async def test_user() -> None:
    """Test User."""
    # Get collection `User`.
    user_coll = await Scruby.collection(User)

    # collection_name
    assert user_coll.collection_name() == "User"

    # collection_list
    for coll_name in await Scruby.collection_list():
        assert coll_name in ["User", "Phone", "Car"]

    # estimated_document_count
    assert await user_coll.estimated_document_count() == 9
    # count_documents
    assert user_coll.count_documents(filter_fn=lambda doc: doc.first_name == "John") == 9

    # add_doc
    user = User(
        first_name="John",
        last_name="Smith",
        birthday=datetime(1970, 1, 1, tzinfo=ZoneInfo("UTC")),
        email="John_Smith@gmail.com",
        phone="+447986123459",
    )
    await user_coll.add_doc(user)
    assert await user_coll.estimated_document_count() == 10
    assert user_coll.count_documents(filter_fn=lambda doc: doc.first_name == "John") == 10

    # update_doc and get_doc
    user = User(
        first_name="John",
        last_name="Smith",
        birthday=datetime(1972, 11, 7, tzinfo=ZoneInfo("UTC")),
        email="John_Smith@gmail.com",
        phone="+447986123459",
    )
    await user_coll.update_doc(user)
    user: User | None = user_coll.get_doc("+447986123459")
    assert user is not None
    assert user.birthday == datetime(1972, 11, 7, tzinfo=ZoneInfo("UTC"))

    # has_key
    assert user_coll.has_key("+447986123459")

    # delete_doc
    await user_coll.delete_doc("+447986123459")
    assert not user_coll.has_key("+447986123459")
    assert await user_coll.estimated_document_count() == 9
    assert user_coll.count_documents(filter_fn=lambda doc: doc.first_name == "John") == 9

    # find_one
    # ReturnType MODEL
    user = user_coll.find_one(filter_fn=lambda doc: doc.phone == "+447986123459")
    assert user is None
    user = user_coll.find_one(filter_fn=lambda doc: doc.phone == "+447986123457")
    assert user is not None
    assert isinstance(user, User)
    assert user.phone == "+447986123457"
    # ReturnType JSON
    user = user_coll.find_one(
        filter_fn=lambda doc: doc.phone == "+447986123457",
        return_type=ReturnType.JSON,
    )
    assert user is not None
    assert isinstance(user, str)
    user = User.model_validate_json(user)
    assert user.phone == "+447986123457"
    # ReturnType DICT
    user = user_coll.find_one(
        filter_fn=lambda doc: doc.phone == "+447986123457",
        return_type=ReturnType.DICT,
    )
    assert user is not None
    assert isinstance(user, dict)
    user = User.model_validate(user)
    assert user.phone == "+447986123457"

    # find_many
    # ReturnType MODEL
    users = user_coll.find_many(filter_fn=lambda doc: doc.first_name == "???")
    assert users is None
    users = user_coll.find_many()
    assert users is not None
    assert len(users) == 9
    users = user_coll.find_many(filter_fn=lambda doc: doc.first_name == "John")
    assert users is not None
    assert len(users) == 9
    # ReturnType JSON
    # ReturnType DICT

    # update_many
    count_updated = await user_coll.update_many(
        new_data={"first_name": "???", "last_name": "???"},
        filter_fn=lambda doc: doc.first_name == "???" or doc.last_name == "???",
    )
    assert count_updated == 0
    count_updated = await user_coll.update_many(
        new_data={"first_name": "Gene", "last_name": "Kost"},
        filter_fn=lambda doc: doc.first_name == "John" or doc.last_name == "Smith",
    )
    assert count_updated == 9
    for user in user_coll.find_many():
        assert user.first_name == "Gene"
        assert user.last_name == "Kost"
    count_updated = await user_coll.update_many(
        new_data={"first_name": "John", "last_name": "Smith"},
        filter_fn=lambda doc: doc.first_name == "Gene" or doc.last_name == "Kost",
    )
    assert count_updated == 9
    for user in user_coll.find_many():
        assert user.first_name == "John"
        assert user.last_name == "Smith"

    # delete_many
    count_deleted = await user_coll.delete_many(filter_fn=lambda doc: doc.phone == "???")
    assert count_deleted == 0
    count_deleted = await user_coll.delete_many(
        filter_fn=lambda doc: doc.phone == "+447986123455" or doc.phone == "+447986123453",
    )
    assert count_deleted == 2
    users = user_coll.find_many()
    assert len(users) == 7
    for user in users:
        assert user.phone != "+447986123455"
        assert user.phone != "+447986123453"

    #
    # delete_collection
    await Scruby.delete_collection("User")
    assert DocCache.cache.get("User") is None
    for coll_name in await Scruby.collection_list():
        assert coll_name in ["Phone", "Car"]
    user_coll = await Scruby.collection(User)
    assert await user_coll.estimated_document_count() == 0
    assert user_coll.count_documents(filter_fn=lambda doc: doc.first_name == "John") == 0
    assert DocCache.cache.get("User") is not None
    for coll_name in await Scruby.collection_list():
        assert coll_name in ["User", "Phone", "Car"]


async def test_phone() -> None:
    """Test Phone."""
    # Get collection `Phone`.
    phone_coll = await Scruby.collection(Phone)

    # collection_name
    assert phone_coll.collection_name() == "Phone"

    # collection_list
    for coll_name in await Scruby.collection_list():
        assert coll_name in ["User", "Phone", "Car"]

    # estimated_document_count
    assert await phone_coll.estimated_document_count() == 9
    # count_documents
    assert phone_coll.count_documents(filter_fn=lambda doc: doc.brand == "Samsung") == 9

    # add_doc
    phone = Phone(
        brand="Samsung",
        model="Galaxy A26 9",
        screen_diagonal=6.7,
        matrix_type="Super AMOLED",
    )
    await phone_coll.add_doc(phone)
    assert await phone_coll.estimated_document_count() == 10
    assert phone_coll.count_documents(filter_fn=lambda doc: doc.brand == "Samsung") == 10

    # update_doc and get_doc
    phone = Phone(
        brand="Samsung",
        model="Galaxy A26 9",
        screen_diagonal=10.2,
        matrix_type="Super AMOLED",
    )
    await phone_coll.update_doc(phone)
    phone = phone_coll.get_doc("Samsung:Galaxy A26 9")
    assert phone is not None
    assert phone.screen_diagonal == pytest.approx(10.2)

    # has_key
    assert phone_coll.has_key("Samsung:Galaxy A26 9")

    # delete_doc
    await phone_coll.delete_doc("Samsung:Galaxy A26 9")
    assert not phone_coll.has_key("Samsung:Galaxy A26 9")
    assert await phone_coll.estimated_document_count() == 9
    assert phone_coll.count_documents(filter_fn=lambda doc: doc.brand == "Samsung") == 9

    # find_one
    # ReturnType MODEL
    phone = phone_coll.find_one(filter_fn=lambda doc: doc.model == "Galaxy A26 9")
    assert phone is None
    phone = phone_coll.find_one(filter_fn=lambda doc: doc.model == "Galaxy A26 7")
    assert phone is not None
    assert phone.model == "Galaxy A26 7"
    # ReturnType JSON
    phone = phone_coll.find_one(
        filter_fn=lambda doc: doc.model == "Galaxy A26 7",
        return_type=ReturnType.JSON,
    )
    assert phone is not None
    assert isinstance(phone, str)
    phone = Phone.model_validate_json(phone)
    assert phone.model == "Galaxy A26 7"
    # ReturnType DICT
    phone = phone_coll.find_one(
        filter_fn=lambda doc: doc.model == "Galaxy A26 7",
        return_type=ReturnType.DICT,
    )
    assert phone is not None
    assert isinstance(phone, dict)
    phone = Phone.model_validate(phone)
    assert phone.model == "Galaxy A26 7"

    # find_many
    # ReturnType MODEL
    phones = phone_coll.find_many(filter_fn=lambda doc: doc.matrix_type == "???")
    assert phones is None
    phones = phone_coll.find_many()
    assert phones is not None
    assert len(phones) == 9
    phones = phone_coll.find_many(filter_fn=lambda doc: doc.matrix_type == "Super AMOLED")
    assert phones is not None
    assert len(phones) == 9
    # ReturnType JSON
    # ReturnType DICT

    # update_many
    count_updated = await phone_coll.update_many(
        new_data={"brand": "???"},
        filter_fn=lambda doc: doc.brand == "???",
    )
    assert count_updated == 0
    count_updated = await phone_coll.update_many(
        new_data={"brand": "SONY"},
        filter_fn=lambda doc: doc.brand == "Samsung",
    )
    assert count_updated == 9
    for phone in phone_coll.find_many():
        assert phone.brand == "SONY"
    count_updated = await phone_coll.update_many(
        new_data={"brand": "Samsung"},
        filter_fn=lambda doc: doc.brand == "SONY",
    )
    assert count_updated == 9
    for phone in phone_coll.find_many():
        assert phone.brand == "Samsung"

    # delete_many
    count_deleted = await phone_coll.delete_many(filter_fn=lambda doc: doc.model == "???")
    assert count_deleted == 0
    count_deleted = await phone_coll.delete_many(
        filter_fn=lambda doc: doc.model == "Galaxy A26 5" or doc.model == "Galaxy A26 3",
    )
    assert count_deleted == 2
    phones = phone_coll.find_many()
    assert len(phones) == 7
    for phone in phones:
        assert phone.model != "Galaxy A26 5"
        assert phone.model != "Galaxy A26 3"

    #
    # delete_collection
    await Scruby.delete_collection("Phone")
    assert DocCache.cache.get("Phone") is None
    for coll_name in await Scruby.collection_list():
        assert coll_name in ["User", "Car"]
    phone_coll = await Scruby.collection(Phone)
    assert await phone_coll.estimated_document_count() == 0
    assert phone_coll.count_documents(filter_fn=lambda doc: doc.brand == "Samsung") == 0
    assert DocCache.cache.get("Phone") is not None
    for coll_name in await Scruby.collection_list():
        assert coll_name in ["User", "Phone", "Car"]


async def test_car() -> None:
    """Test Car."""
    # Get collection `Car`.
    car_coll = await Scruby.collection(Car)

    # collection_name
    assert car_coll.collection_name() == "Car"

    # collection_list
    for coll_name in await Scruby.collection_list():
        assert coll_name in ["User", "Phone", "Car"]

    # estimated_document_count
    assert await car_coll.estimated_document_count() == 9
    # count_documents
    assert car_coll.count_documents(filter_fn=lambda doc: doc.brand == "Mazda") == 9

    # add_doc
    car = Car(
        brand="Mazda",
        model="EZ-6 9",
        year=2025,
        power_reserve=600,
    )
    await car_coll.add_doc(car)
    assert await car_coll.estimated_document_count() == 10
    assert car_coll.count_documents(filter_fn=lambda doc: doc.brand == "Mazda") == 10

    # update_doc and get_doc
    car = Car(
        brand="Mazda",
        model="EZ-6 9",
        year=2025,
        power_reserve=800,
    )
    await car_coll.update_doc(car)
    car = car_coll.get_doc("Mazda:EZ-6 9")
    assert car is not None
    assert car.power_reserve == 800

    # has_key
    assert car_coll.has_key("Mazda:EZ-6 9")

    # delete_doc
    await car_coll.delete_doc("Mazda:EZ-6 9")
    assert not car_coll.has_key("Mazda:EZ-6 9")
    assert await car_coll.estimated_document_count() == 9
    assert car_coll.count_documents(filter_fn=lambda doc: doc.brand == "Mazda") == 9

    # find_one
    # ReturnType MODEL
    car = car_coll.find_one(filter_fn=lambda doc: doc.model == "EZ-6 9")
    assert car is None
    car = car_coll.find_one(filter_fn=lambda doc: doc.model == "EZ-6 7")
    assert car is not None
    assert car.model == "EZ-6 7"
    # ReturnType JSON
    car = car_coll.find_one(
        filter_fn=lambda doc: doc.model == "EZ-6 7",
        return_type=ReturnType.JSON,
    )
    assert car is not None
    assert isinstance(car, str)
    car = Car.model_validate_json(car)
    assert car.model == "EZ-6 7"
    # ReturnType DICT
    car = car_coll.find_one(
        filter_fn=lambda doc: doc.model == "EZ-6 7",
        return_type=ReturnType.DICT,
    )
    assert car is not None
    assert isinstance(car, dict)
    car = Car.model_validate(car)
    assert car.model == "EZ-6 7"

    # find_many
    # ReturnType MODEL
    cars = car_coll.find_many(filter_fn=lambda doc: doc.power_reserve == 800)
    assert cars is None
    cars = car_coll.find_many()
    assert cars is not None
    assert len(cars) == 9
    cars = car_coll.find_many(filter_fn=lambda doc: doc.power_reserve == 600)
    assert cars is not None
    assert len(cars) == 9
    # ReturnType JSON
    # ReturnType DICT

    # update_many
    count_updated = await car_coll.update_many(
        new_data={"brand": "???"},
        filter_fn=lambda doc: doc.brand == "???",
    )
    assert count_updated == 0
    count_updated = await car_coll.update_many(
        new_data={"brand": "BMW"},
        filter_fn=lambda doc: doc.brand == "Mazda",
    )
    assert count_updated == 9
    for car in car_coll.find_many():
        assert car.brand == "BMW"
    count_updated = await car_coll.update_many(
        new_data={"brand": "Mazda"},
        filter_fn=lambda doc: doc.brand == "BMW",
    )
    assert count_updated == 9
    for car in car_coll.find_many():
        assert car.brand == "Mazda"

    # delete_many
    count_deleted = await car_coll.delete_many(filter_fn=lambda doc: doc.model == "???")
    assert count_deleted == 0
    count_deleted = await car_coll.delete_many(
        filter_fn=lambda doc: doc.model == "EZ-6 5" or doc.model == "EZ-6 3",
    )
    assert count_deleted == 2
    cars = car_coll.find_many()
    assert len(cars) == 7
    for car in cars:
        assert car.model != "EZ-6 5"
        assert car.model != "EZ-6 3"

    #
    # delete_collection
    await Scruby.delete_collection("Car")
    assert DocCache.cache.get("Car") is None
    for coll_name in await Scruby.collection_list():
        assert coll_name in ["User", "Phone"]
    car_coll = await Scruby.collection(Car)
    assert await car_coll.estimated_document_count() == 0
    assert car_coll.count_documents(filter_fn=lambda doc: doc.brand == "Mazda") == 0
    assert DocCache.cache.get("Car") is not None
    for coll_name in await Scruby.collection_list():
        assert coll_name in ["User", "Phone", "Car"]
    #
    # Delete DB.
    Scruby.napalm()
