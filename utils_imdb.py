"""
utils_imdb.py — IMDb lookup helpers (get_poster / get_poster2), split out of
utils.py. See utils_state.py for the module-split overview.
"""

import re
import logging

from info import *
from utils_state import imdb
from utils_helpers import list_to_str

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def get_poster(query, bulk=False, id=False, file=None):
    if DEBUG_MODE:
        logger.info(
            "[IMDB] get_poster entered | query=%r | bulk=%s | id=%s | file=%r",
            query, bulk, id, file
        )

    if not id:
        query = (query.strip()).lower()
        title = query
        if DEBUG_MODE:
            logger.info("[IMDB] normalized query=%r", query)

        year = re.findall(r'[1-2]\d{3}$', query, re.IGNORECASE)
        if year:
            year = list_to_str(year[:1])
            title = (query.replace(year, "")).strip()
            if DEBUG_MODE:
                logger.info("[IMDB] trailing year detected=%r | title=%r", year, title)
        elif file is not None:
            year = re.findall(r'[1-2]\d{3}', file, re.IGNORECASE)
            if year:
                year = list_to_str(year[:1])
                if DEBUG_MODE:
                    logger.info("[IMDB] year inferred from file=%r", year)
        else:
            year = None
            if DEBUG_MODE:
                logger.info("[IMDB] no year detected")

        if DEBUG_MODE:
            logger.info("[IMDB] searching movie title=%r", title.lower())

        movieid = imdb.search_movie(title.lower(), results=10)

        if DEBUG_MODE:
            logger.info("[IMDB] search_movie returned count=%s", len(movieid) if movieid else 0)

        if not movieid:
            if DEBUG_MODE:
                logger.info("[IMDB] no search results for query=%r", query)
            return None

        if year:
            filtered = list(filter(lambda k: str(k.get('year')) == str(year), movieid))
            if DEBUG_MODE:
                logger.info(
                    "[IMDB] year filter applied=%r | before=%s | after=%s",
                    year,
                    len(movieid),
                    len(filtered)
                )
            if not filtered:
                filtered = movieid
                if DEBUG_MODE:
                    logger.info("[IMDB] year filter empty, falling back to original results")
        else:
            filtered = movieid

        movieid = list(filter(lambda k: k.get('kind') in ['movie', 'tv series'], filtered))
        if DEBUG_MODE:
            logger.info(
                "[IMDB] kind filter applied | before=%s | after=%s",
                len(filtered),
                len(movieid)
            )
        if not movieid:
            movieid = filtered
            if DEBUG_MODE:
                logger.info("[IMDB] kind filter empty, falling back to filtered results")

        if bulk:
            if DEBUG_MODE:
                logger.info("[IMDB] bulk=True returning count=%s", len(movieid) if movieid else 0)
            return movieid if movieid else None

        movieid = movieid[0].movieID
        if DEBUG_MODE:
            logger.info("[IMDB] selected movieid=%s", movieid)
    else:
        movieid = query
        if DEBUG_MODE:
            logger.info("[IMDB] id=True using direct movieid=%s", movieid)

    movie = imdb.get_movie(movieid)
    if DEBUG_MODE:
        logger.info("[IMDB] get_movie fetched=%s", bool(movie))
    if not movie:
        if DEBUG_MODE:
            logger.info("[IMDB] movie not found for movieid=%s", movieid)
        return None

    date = movie.get("original air date") or movie.get("year") or "N/A"
    plot = ""
    if not LONG_IMDB_DESCRIPTION:
        plot = movie.get('plot')
        if plot and len(plot) > 0:
            plot = plot[0]
        if DEBUG_MODE:
            logger.info("[IMDB] plot source=plot | length=%s", len(plot) if plot else 0)
    else:
        plot = movie.get('plot outline')
        if DEBUG_MODE:
            logger.info("[IMDB] plot source=plot outline | length=%s", len(plot) if plot else 0)
    if plot and len(plot) > 800:
        if DEBUG_MODE:
            logger.info("[IMDB] truncating plot from %s to 800 chars", len(plot))
        plot = plot[:800] + "..."

    result = {
        'title': movie.get('title'),
        'votes': movie.get('votes'),
        "aka": list_to_str(movie.get("akas")),
        "seasons": movie.get("number of seasons"),
        "box_office": movie.get('box office'),
        'localized_title': movie.get('localized title'),
        'kind': movie.get("kind"),
        "imdb_id": f"tt{movie.get('imdbID')}",
        "cast": list_to_str(movie.get("cast")),
        "runtime": list_to_str(movie.get("runtimes")),
        "countries": list_to_str(movie.get("countries")),
        "certificates": list_to_str(movie.get("certificates")),
        "languages": list_to_str(movie.get("languages")),
        "director": list_to_str(movie.get("director")),
        "writer": list_to_str(movie.get("writer")),
        "producer": list_to_str(movie.get("producer")),
        "composer": list_to_str(movie.get("composer")),
        "cinematographer": list_to_str(movie.get("cinematographer")),
        "music_team": list_to_str(movie.get("music department")),
        "distributors": list_to_str(movie.get("distributors")),
        'release_date': date,
        'year': movie.get('year'),
        'genres': list_to_str(movie.get("genres")),
        'poster': movie.get('full-size cover url'),
        'plot': plot,
        'rating': str(movie.get("rating")),
        'url': f'https://www.imdb.com/title/tt{movieid}'
    }

    if DEBUG_MODE:
        logger.info(
            "[IMDB] result ready | title=%r | year=%r | kind=%r | poster=%s",
            result.get("title"),
            result.get("year"),
            result.get("kind"),
            bool(result.get("poster")),
        )

    return result


async def get_poster2(query, bulk=False, id=False, file=None):
    if DEBUG_MODE:
        logger.info(
            "[IMDB2] get_poster2 entered | query=%r | bulk=%s | id=%s | file=%r",
            query, bulk, id, file
        )

    if not id:
        query = (query.strip()).lower()
        title = query
        if DEBUG_MODE:
            logger.info("[IMDB2] normalized query=%r", query)

        year = re.findall(r'[1-2]\d{3}$', query, re.IGNORECASE)
        if year:
            year = list_to_str(year[:1])
            title = (query.replace(year, "")).strip()
            if DEBUG_MODE:
                logger.info("[IMDB2] trailing year detected=%r | title=%r", year, title)
        elif file is not None:
            year = re.findall(r'[1-2]\d{3}', file, re.IGNORECASE)
            if year:
                year = list_to_str(year[:1])
                if DEBUG_MODE:
                    logger.info("[IMDB2] year inferred from file=%r", year)
        else:
            year = None
            if DEBUG_MODE:
                logger.info("[IMDB2] no year detected")

        if DEBUG_MODE:
            logger.info("[IMDB2] searching movie title=%r", title.lower())

        movieid = imdb.search_movie(title.lower(), results=10)
        if DEBUG_MODE:
            logger.info("[IMDB2] search_movie returned count=%s", len(movieid) if movieid else 0)

        if not movieid:
            if DEBUG_MODE:
                logger.info("[IMDB2] no search results for query=%r", query)
            return None

        if year:
            filtered = list(filter(lambda k: str(k.get('year')) == str(year), movieid))
            if DEBUG_MODE:
                logger.info(
                    "[IMDB2] year filter applied=%r | before=%s | after=%s",
                    year,
                    len(movieid),
                    len(filtered)
                )
            if not filtered:
                filtered = movieid
                if DEBUG_MODE:
                    logger.info("[IMDB2] year filter empty, falling back to original results")
        else:
            filtered = movieid

        movieid = list(filter(lambda k: k.get('kind') in ['movie', 'tv series'], filtered))
        if DEBUG_MODE:
            logger.info(
                "[IMDB2] kind filter applied | before=%s | after=%s",
                len(filtered),
                len(movieid)
            )
        if not movieid:
            movieid = filtered
            if DEBUG_MODE:
                logger.info("[IMDB2] kind filter empty, falling back to filtered results")

        if bulk:
            if DEBUG_MODE:
                logger.info("[IMDB2] bulk=True returning count=%s", len(movieid) if movieid else 0)
            return movieid

        movieid = movieid[0].movieID
        if DEBUG_MODE:
            logger.info("[IMDB2] selected movieid=%s", movieid)
    else:
        movieid = query
        if DEBUG_MODE:
            logger.info("[IMDB2] id=True using direct movieid=%s", movieid)

    movie = imdb.get_movie(movieid)
    if DEBUG_MODE:
        logger.info("[IMDB2] get_movie fetched=%s", bool(movie))
    if movie.get("original air date"):
        date = movie["original air date"]
    elif movie.get("year"):
        date = movie.get("year")
    else:
        date = "N/A"

    plot = ""
    if not LONG_IMDB_DESCRIPTION:
        plot = movie.get('plot')
        if plot and len(plot) > 0:
            plot = plot[0]
        if DEBUG_MODE:
            logger.info("[IMDB2] plot source=plot | length=%s", len(plot) if plot else 0)
    else:
        plot = movie.get('plot outline')
        if DEBUG_MODE:
            logger.info("[IMDB2] plot source=plot outline | length=%s", len(plot) if plot else 0)
    if plot and len(plot) > 800:
        if DEBUG_MODE:
            logger.info("[IMDB2] truncating plot from %s to 800 chars", len(plot))
        plot = plot[0:800] + "..."

    result = {
        'title': movie.get('title'),
        'votes': movie.get('votes'),
        "aka": list_to_str(movie.get("akas")),
        "seasons": movie.get("number of seasons"),
        "box_office": movie.get('box office'),
        'localized_title': movie.get('localized title'),
        'kind': movie.get("kind"),
        "imdb_id": f"tt{movie.get('imdbID')}",
        "cast": list_to_str(movie.get("cast")),
        "runtime": list_to_str(movie.get("runtimes")),
        "countries": list_to_str(movie.get("countries")),
        "certificates": list_to_str(movie.get("certificates")),
        "languages": list_to_str(movie.get("languages")),
        "director": list_to_str(movie.get("director")),
        "writer": list_to_str(movie.get("writer")),
        "producer": list_to_str(movie.get("producer")),
        "composer": list_to_str(movie.get("composer")),
        "cinematographer": list_to_str(movie.get("cinematographer")),
        "music_team": list_to_str(movie.get("music department")),
        "distributors": list_to_str(movie.get("distributors")),
        'release_date': date,
        'year': movie.get('year'),
        'genres': list_to_str(movie.get("genres")),
        'poster': movie.get('full-size cover url'),
        'plot': plot,
        'rating': str(movie.get("rating")),
        'url': f'https://www.imdb.com/title/tt{movieid}'
    }

    if DEBUG_MODE:
        logger.info(
            "[IMDB2] result ready | title=%r | year=%r | kind=%r | poster=%s",
            result.get("title"),
            result.get("year"),
            result.get("kind"),
            bool(result.get("poster")),
        )

    return result
