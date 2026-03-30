def IS_CONSTRUCT(ctx, target):
    return getattr(target, "type", None) == "construct"

def IS_OBJECT(ctx, target):
    return getattr(target, "type", None) == "object"

def NOT_IN_PARTY(ctx, target):
    return target not in getattr(ctx.source, "party", set())

def IS_MATERIAL(ctx, target):
    return getattr(target, "type", None) == "material"
