# **fufufilms**
---

Python script that utilizes the tmdbsimple, omdb, and SendGrid (optional) APIs to return a list of highly-rated films (top rated, in-theaters, popular, etc).

*"Highly-rated" is interpreted as an IMDB rating >= 7.5 (out of 10) and a Metacritic rating >= 75 (out of 100).*

1. First off, set up your Python environment; acquire the necessary Python packages

- `pip install tmdbsimple`
- `pip install omdb`
- `pip install sendgrid`

2. Get your FREE API keys:

- For TMDBSimple, go to https://www.themoviedb.org/
- For OMDB, go to https://www.omdbapi.com/
- For SendGrid, go to https://sendgrid.com/

3. Input your newly acquired API key values into "fufufilms.py".

## optional (1)

The script currently returns top-rated films.
You can tweak this. For example, you can start from a different set of films by using one of the following:

`response = tmdb_movies.now_playing()`

*or*

`response = tmdb_movies.upcoming()`

## optional (2)

I created a process in Windows Task Scheduler that runs "fufufilms.py" once a month.  This monthly task is the reason I implemented a SendGrid function to send the final films list to target email addresses - Hooray! for spamming friends and family :).

*ENJOY! and tweak to your liking!*