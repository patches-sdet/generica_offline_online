def tagged(tag: str):
    return lambda ctx, target: tag in getattr(target, "tags", set())
