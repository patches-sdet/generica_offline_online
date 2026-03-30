def rebuild_tags(character, effects=None):
    tags = set()

    # Race
    tags.update(character.race.tags)

    # Adventure jobs
    for job in character.adventure_jobs:
        tags.update(job.tags)

    # Professions (if present)
    for job in character.profession_jobs:
        tags.update(getattr(job, "tags", []))

    character.tags = tags
