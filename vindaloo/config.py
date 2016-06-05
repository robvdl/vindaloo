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


def configure_auth_settings(settings):
    """
    Sets up the auth configuration based on the application .ini file
    settings and provides default settings where things are missing.

    :param settings: Pyramid settings dict.
    """
    # The password algorithm either pbkdf2_sha256, pbkdf2_sha512 or bcrypt.
    settings['vindaloo.auth.hashalg'] = settings.get('vindaloo.auth.hashalg', 'pbkdf2_sha256')

    # The rounds parameter is optional but still needs to be converted to int.
    if 'vindaloo.auth.rounds' in settings:
        settings['vindaloo.auth.rounds'] = int(settings['vindaloo.auth.rounds'])
