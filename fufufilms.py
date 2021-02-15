'''
Created by fufufanatic
fufufilms creates a list of awesome movies (based on imdb and metacritic ratings) that can be sent to friends
'''

import os
import tmdbsimple
import omdb
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Email, Content, Mail

# Gets the necessary API keys, currently set as environment variables
tmdb_key = os.environ.get('tmdb_key')
omdb_key = os.environ.get('omdb_key')
sg_key = os.environ.get('sg_key')

# Gets the necessary email addresses, currently set as environment variables
my_email = os.environ.get('my_email')
target_emails = os.environ.get('target_emails')

def get_films():
    
    # Returns a list of films based on a custom TMDB query
    print('\n=============== [TMDB] Films Based on Custom Query [TMDB] ===============\n')
    
    tmdb_films = []
    tmdbsimple.API_KEY = tmdb_key
    tmdb_movies = tmdbsimple.Movies()
    
    # Customizable tmdb films query that populates a results list
    count = 1
    while tmdb_movies.top_rated(page=count)['results']:
        films = tmdb_movies.top_rated(page=count)['results']
        for film in films:
            release_date = int(film['release_date'][0:4])
            # only select movies released within a given year range
            if 2019 < release_date < 2022:
                print(film, '\n')
                tmdb_films.append(film)
        count += 1

    # Returns film results with stock TMDB ratings, which I don't trust yet :(
    return tmdb_films 

def get_films_with_relevant_ratings(films):
    
    # Returns a list of films that might have ratings (IMDB and RT) I can trust, for now :)
    print('\n=============== [OMDB] Films with Relevant Ratings [OMDB] ===============\n')
    
    films_with_relevant_ratings = []
    for film in films:
        
        # Queries OMDB for a given film title (and year)
        try:
            film_json = omdb.request(apikey=omdb_key, t=film['title'], y=film['release_date'][0:4]).json()
        except Exception:
            continue
        
        # If movie not found or has no ratings, then continue to next movie search
        if 'Error' in film_json or not film_json['Ratings']:
            continue

        # Print the movie details for testing purposes
        print(film_json['Title'], film_json['Year'], film_json['Ratings'])

        # Creates a stock dictionary object for said film and initializes its ratings to zero; these remain zero if a rating has not been given  
        film_rating_dict = {}
        film_rating_dict['title'] = film_json['Title']
        film_rating_dict['year'] = film_json['Year']
        film_rating_dict['imdb rating'] = 0  
        film_rating_dict['meta rating'] = 0
        
        film_ratings = film_json['Ratings']
        # Iterates through all available ratings (IMDB, RT, Metacritic, etc.), but I only care for IMDB and Metacritic
        for film_rating in film_ratings: 
            if film_rating['Source'] == 'Internet Movie Database':
                # For example, an IMDB rating of 7.1/10 is returned as 7.1
                imdb_rating = float(film_rating['Value'][:-3])
                print(imdb_rating) 
                film_rating_dict['imdb rating'] = imdb_rating
            if film_rating['Source'] == 'Metacritic':
                # For example, a Metacritic rating of 70/100 is returned as 70
                meta_rating = int(film_rating['Value'][:-4]) 
                print(meta_rating)
                film_rating_dict['meta rating'] = meta_rating
        
        # The final film-dictionary object is added to a list for "worthiness" consideration
        films_with_relevant_ratings.append(film_rating_dict) 
              
    return films_with_relevant_ratings
    
def get_fufufilms(films_with_relevant_ratings):
    
    # Returns a list of worthy films based on MY criteria (solely IMDB and RT ratings)
    print('\n=============== [FUFU] Films Considered Worthy!!! [FUFU] ===============\n')

    fufu_films = []
    
    for film in films_with_relevant_ratings:
        
        title = film['title']
        year = film['year']
        imdb = film['imdb rating']
        meta = film['meta rating']
        
        if (imdb >= 7.5) and (meta >= 75):
            # Puts worthy film into tuple format, for example (Home Alone, 1990), and adds the tuple to the final list
            fufu_film = (title, year)
            fufu_films.append(fufu_film) 

    # Sorts the worthy list based on movie release year, oldest to most recent
    fufu_films.sort(key=lambda x:x[1], reverse=False)
    return fufu_films

def send_fufufilms(fufu_films):
    
    # Shoots an email containing worthy films, using the SendGrid API
    print('\n=============== Sending an Email Containing Worthy Films!!! ===============\n')
    
    # Packs all worthy films into one neat string
    fufu_films_str = ''
    for film in fufu_films:
        fufu_films_str += f' - {film[0]} ({film[1]})\r\n'
    
    # Print function to test output
    print(fufu_films_str) 
    
    # Email creation and dispatch; standard stuff swiped from the SendGrid tutorial
    message = Mail(
        from_email = my_email,
        to_emails = target_emails,
        subject = 'Film (by fufufanatic)',
        plain_text_content = fufu_films_str)

    sg = SendGridAPIClient(sg_key)
    response = sg.send(message)
    
    # Print function to test status of sent message
    print(response.status_code)
    print(response.body)
    print(response.headers)
    
def main():
    
    films = get_films()
    films_with_relevant_ratings = get_films_with_relevant_ratings(films)
    fufufilms = get_fufufilms(films_with_relevant_ratings)

    for film in fufufilms:
        print(f'{film[0]} ({film[1]})')
    
    #send_fufufilms(fufufilms)
      
if __name__ == '__main__':
    main()