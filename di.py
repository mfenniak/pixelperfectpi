from dependency_injector import containers, providers
from data.purpleair import PurpleAirDataResolver
from pixelperfectpi import Clock

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    purpleair = providers.Singleton(
        PurpleAirDataResolver,
        url=config.purpleair.url,
    )

    clock = providers.Singleton(
        Clock,
        purpleair=purpleair,
    )
