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
from typing import Any, Annotated
from pydantic import Field
from scruby import Scruby, ScrubyModel
from scruby_plugin import ScrubyPlugin
from pprint import pprint as pp


# Create plugin
class CollectionMeta(ScrubyPlugin):
    def __init__(self, scruby: Any) -> None:
        ScrubyPlugin.__init__(self, scruby)

    async def get(self) -> Any:
        scruby = self.scruby()
        return await scruby.get_meta()


class Car(ScrubyModel):
    """Car model."""
    brand: Annotated[str, Field(frozen=True)]
    model: Annotated[str, Field(frozen=True)]
    year: int
    power_reserve: int
    # key is always at bottom
    key: Annotated[
        str,
        Field(
            frozen=True,
            default_factory=lambda data: f"{data['brand']}:{data['model']}",
        ),
    ]


async def main() -> None:
    """Example."""
    # Activate database.
    Scruby.run(plugins=[CollectionMeta])

    # Get collection `Car`.
    car_coll = Scruby(Car)
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
