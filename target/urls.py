def register_urls(app):
    from app.apis import urls

    app.register_blueprint(urls)
