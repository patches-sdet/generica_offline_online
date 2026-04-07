def IS_ENEMY(ctx, target):
    return target not in ctx.source.party

def IS_ALLY(ctx, target):
    return target in ctx.source.party
