#### Installation

```shell
uv add scruby-plugin
```

#### Usage

```py title="main.py" linenums="1"
from typing import Any
from scruby_plugin import ScrubyPlugin

class PluginName(ScrubyPlugin):
    def __init__(self, scruby: Any) -> None:
        ScrubyPlugin.__init__(self, scruby)

    ...your code...
```

#### Example

```py title="main.py" linenums="1"
import anyio
from typing import Any
from pydantic import Field
from scruby import Scruby, ScrubyModel, settings
from scruby_plugin import ScrubyPlugin
from pprint import pprint as pp


# Create plugin
class CollectionMeta(ScrubyPlugin):
    def __init__(self, scruby: Any) -> None:
        ScrubyPlugin.__init__(self, scruby)

    async def get(self) -> Any:
        scruby = self.scruby()
        return await scruby.get_meta()


# Plugins connection.
settings.PLUGINS = [
    CollectionMeta,
]


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


async def main() -> None:
    # Get collection `Car`.
    car_coll = await Scruby.collection(Car)
    # Get metadata of collection
    meta = await car_coll.plugins.collectionMeta.get()
    # Print to console
    pp(meta)
    #
    # Full database deletion.
    # Hint: The main purpose is tests.
    Scruby.napalm()

if __name__ == "__main__":
    anyio.run(main)
```
