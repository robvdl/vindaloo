def add_api(config, api):
    """
    Adds an Api instance to the Pyramid Configurator, therefore adding
    routes and views for resources and services registered with that Api.

    :param config: Pyramid Configurator object.
    :param api: Api instance.
    """
    def callback():
        api.register(config)
        config.commit()

    # multiple Api objects can be added, so include it in the discriminator
    discriminator = ('add_api', api)
    config.action(discriminator, callable=callback)
