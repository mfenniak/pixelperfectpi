from dependency_injector import containers, providers
from data.purpleair import PurpleAirDataResolver
from data.envcanada import EnvironmentCanadaDataResolver
from pixelperfectpi import Clock

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    purpleair = providers.Singleton(
        PurpleAirDataResolver,
        url=config.purpleair.url,
    )

    env_canada = providers.Singleton(EnvironmentCanadaDataResolver)

    clock = providers.Singleton(
        Clock,
        purpleair=purpleair,
        env_canada=env_canada,
    )
