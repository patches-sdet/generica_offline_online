def IS_CONSTRUCT(ctx, target):
    return getattr(target, "type", None) == "construct"
