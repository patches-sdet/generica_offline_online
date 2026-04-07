def HAS_STATE(state):
    return lambda ctx, target: state in getattr(target, "states", {})

def IS_SURPRISED(ctx, target):
    return "surprised" in getattr(target, "states", {})

def IS_HELPLESS(ctx, target):
    return "helpless" in getattr(target, "states", {})

def IS_LYING(ctx, target):
    return "lying" in getattr(target, "states", {})

def HAGGLING(ctx, target):
    return "haggling" in getattr(target, "states", {})