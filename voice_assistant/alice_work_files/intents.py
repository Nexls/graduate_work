HELP = 'help'
DETAILS = 'details'

TOP_BY_TYPE = 'top_by_type'
TOP_BY_GENRE = 'top_by_genre'
TOP_BY_RELEASE_DATE = 'top_by_release_date'

FILM_AUTHOR = 'film_author'
FILM_ACTORS = 'film_actors'
FILM_DESCRIPTION = 'film_description'
FILM_DURATION = 'film_duration'
FILM_GENRE = 'film_genre'
FILM_RATING = 'film_rating'
FILM_RELEASE_DATE = 'film_release_date'

PERSON_AGE = 'person_age'
PERSON_FILMS = 'person_films'
PERSON_BIOGRAPHY = 'person_biography'

# Intent groups
TOP_FILM_INTENTS = [
    TOP_BY_RELEASE_DATE,
    TOP_BY_TYPE,
    TOP_BY_GENRE,
]
FILM_INFO_INTENTS = [
    FILM_AUTHOR,
    FILM_ACTORS,
    FILM_GENRE,
    FILM_RATING,
    FILM_DURATION,
    FILM_RELEASE_DATE,
    FILM_DESCRIPTION,
    DETAILS,
]
PERSON_INFO_INTENTS = [
    PERSON_AGE,
    PERSON_FILMS,
    PERSON_BIOGRAPHY,
    DETAILS,
]