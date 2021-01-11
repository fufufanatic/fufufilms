'''
Created by fufufanatic
The FufuFilms script creates and sends (email) a list of films deemed watch-worthy (solely subjective)
'''

import tmdbsimple
import omdb
from creds import Creds
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Email, Content, Mail

# # Gets the necessary API keys (environment variables) from the BASE python file
tmdb_key = Creds.tmdb_key
omdb_key = Creds.omdb_key
sg_key = Creds.sg_key

# # List of recipients' emails (including mine as the sender)
my_email = Creds.my_email
target_emails = Creds.target_emails

def get_films():
    
    # Returns a list of films based on a custom TMDB query
    print('\n=============== [TMDB] Films Based on Custom Query [TMDB] ===============\n')
    
    tmdbsimple.API_KEY = tmdb_key
    tmdb_films = tmdbsimple.Movies()
    
    # Customizable films-query that populates a results dictionary in response
    response = tmdb_films.now_playing(page=35)
    
    # Print function to test output
    for film in response['results']:
        print(film['title'], film['release_date'])
        
    # Returns film results with stock TMDB ratings, which I don't trust yet :(
    return response['results'] 

def get_films_with_relevant_ratings(films):
    
    # Returns a list of films that might have ratings (IMDB and RT) I can trust, for now :)
    print('\n=============== [OMDB] Films with Relevant Ratings [OMDB] ===============\n')
    
    films_with_relevant_ratings = []
    for film in films:
        
        # Queries OMDB for a given film title (and year)
        film_json = omdb.request(apikey=omdb_key, t=film['title'], y=film['release_date'][0:4]).json() 

        # If movie not found or has no ratings, then continue to next movie search
        if 'Error' in film_json or not film_json['Ratings']:
            continue

        # Print the movie details for testing purposes
        #print(film_json, '\n')
        print(film_json['Title'], film_json['Year'], film_json['Ratings'])

        # Creates a stock dictionary object for said film and initializes its ratings to zero; these remain zero if a rating has not been given  
        film_rating_dict = {}
        film_rating_dict['title'] = film_json['Title']
        film_rating_dict['year'] = film_json['Year']
        film_rating_dict['imdb rating'] = 0  
        film_rating_dict['rt rating'] = 0
        
        film_ratings = film_json['Ratings']
        # Iterates through all available ratings (IMDB, RT, Metacritic, etc.), but I only care for IMDB and RT
        for film_rating in film_ratings: 
            if film_rating['Source'] == 'Internet Movie Database':
                # For example, an IMDB rating of 7/10 is returned as 7
                imdb_rating = float(film_rating['Value'].strip('/10')) 
                film_rating_dict['imdb rating'] = imdb_rating
            if film_rating['Source'] == 'Rotten Tomatoes':
                # For example, an RT rating of 85% is returned as 85
                rt_rating = int(film_rating['Value'].strip('%')) 
                film_rating_dict['rt rating'] = rt_rating
        
        # The final film-dictionary object is added to a list for "worthiness" consideration
        films_with_relevant_ratings.append(film_rating_dict) 
              
    return films_with_relevant_ratings
    
def get_fufufilms(films_with_relevant_ratings):
    
    # Returns a list of worthy films based on MY criteria (solely IMDB and RT ratings)
    print('\n=============== Films Considered Worthy!!! ===============\n')

    fufu_films = []
    
    for film in films_with_relevant_ratings:
        
        title = film['title']
        year = film['year']
        imdb = film['imdb rating']
        rt = film['rt rating']
        
        if (imdb >= 7) and (rt >= 85):
            fufu_film = f'{title} ({year})'
            # Print function to test output
            print(fufu_film)  
            # Film is considered worthy and added to final list
            fufu_films.append(fufu_film) 
       
    return fufu_films

def send_fufufilms(fufu_films):
    
    # Shoots an email containing worthy films, using the SendGrid API
    print('\n=============== Sending an Email Containing Worthy Films!!! ===============\n')
    
    # Packs all worthy films into one neat string
    fufu_films_str = ''
    for film in fufu_films:
        fufu_films_str += f' - {film}\r\n'
    
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
    
    #send_fufufilms(fufufilms)
            
if __name__ == '__main__':
    main()