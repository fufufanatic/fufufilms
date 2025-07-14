'''
fufufilms provides a list of awesome movies (based on IMDB, Metacritic, and Rotten Tomatoes ratings from OMDB API)
'''

import os
import tmdbsimple
import omdb

# Gets the necessary API keys, currently set as environment variables
tmdb_key = os.environ.get('tmdb_key')
print(f"This is my tmdb key: {tmdb_key}")
omdb_key = os.environ.get('omdb_key')
print(f"This is my omdb key: {omdb_key}")
sg_key = os.environ.get('sg_key')
print(f"This is my sendgrid key: {sg_key}")

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
    page_count = 1  # New TMDB API restriction states that "page count must be less than or equal to 500"
    while (page_count <= 500) and (tmdb_movies.top_rated(page=page_count)['results']):
        films = tmdb_movies.top_rated(page=page_count)['results']
        for film in films:
            try:
                release_year = int(film['release_date'][:4])
            except:
                release_year = 0
            # select movies from 2020-2022 to get films with well-established ratings
            if release_year in range(2025, 2026):
                print(film, '\n')
                tmdb_films.append(film)
        page_count += 1

    # Returns film results with stock TMDB ratings, which I don't trust yet :(
    return tmdb_films 

def get_films_with_relevant_ratings(films):
    
    # Returns a list of films that might have ratings (IMDB, Metacritic, and RT)
    print('\n=============== [OMDB] Films with Relevant Ratings [OMDB] ===============\n')
    
    films_with_relevant_ratings = []
    for film in films:
        print(f"\nTrying to find ratings for: {film['title']} ({film['release_date'][:4]})")
        
        # Get OMDB ratings
        try:
            film_json = omdb.request(apikey=omdb_key, t=film['title'], y=film['release_date'][:4], tomatoes='true').json()
        except Exception as e:
            print(f"Error querying OMDB: {str(e)}")
            continue
        else:
            # Print raw API response for debugging
            print("OMDB API Response:")
            print(film_json)
            
            # If movie not found or has no ratings, then continue to next movie search
            if 'Error' in film_json:
                print(f"OMDB Error: {film_json['Error']}")
                continue
            if not film_json.get('Ratings'):
                print("No ratings found in OMDB response")
                continue

        # Create rating dictionary
        film_rating_dict = {}
        film_rating_dict['title'] = film_json['Title']
        film_rating_dict['year'] = film_json['Year']
        film_rating_dict['imdb rating'] = 0
        film_rating_dict['metacritic rating'] = 0
        film_rating_dict['rt rating'] = 0
        
        # Get IMDB, Metacritic, and RT ratings from OMDB
        print("\nAvailable Ratings:")
        film_ratings = film_json['Ratings']
        for film_rating in film_ratings: 
            print(f"{film_rating['Source']}: {film_rating['Value']}")
            
            if film_rating['Source'] == 'Internet Movie Database':
                # IMDB rating (e.g., 7.5/10) -> multiply by 10 to normalize to 100
                imdb_rating = float(film_rating['Value'][:-3]) * 10
                film_rating_dict['imdb rating'] = imdb_rating
            elif film_rating['Source'] == 'Metacritic':
                # Metacritic rating already on scale of 100
                metacritic_rating = int(film_rating['Value'][:-4])
                film_rating_dict['metacritic rating'] = metacritic_rating
            elif film_rating['Source'] == 'Rotten Tomatoes':
                # RT rating (e.g., "98%") -> convert to integer
                rt_rating = int(film_rating['Value'][:-1])
                film_rating_dict['rt rating'] = rt_rating
        
        print("\nExtracted Ratings:")
        print(f"IMDB: {film_rating_dict['imdb rating']}")
        print(f"Metacritic: {film_rating_dict['metacritic rating']}")
        print(f"Rotten Tomatoes: {film_rating_dict['rt rating']}")
        print("----------------------------------------")
        
        # Calculate average rating (only counting ratings that are non-zero)
        ratings = [r for r in [film_rating_dict['imdb rating'], 
                             film_rating_dict['metacritic rating'],
                             film_rating_dict['rt rating']] if r > 0]
        if ratings:  # Only add if we have at least one rating
            film_rating_dict['average rating'] = sum(ratings) / len(ratings)
            films_with_relevant_ratings.append(film_rating_dict)
              
    return films_with_relevant_ratings
    
def get_fufufilms(films_with_relevant_ratings):
    
    # Returns a list of worthy films based on specific rating thresholds
    print('\n=============== [FUFU] Films Meeting All Criteria [FUFU] ===============\n')

    # Sort films by average rating in descending order
    films_with_relevant_ratings.sort(key=lambda x: x['average rating'], reverse=True)
    
    # Take films that meet all rating criteria
    fufu_films = []
    for film in films_with_relevant_ratings:
        if (film['imdb rating'] >= 75 and  # 7.5+ on IMDB (75 after normalization)
            film['metacritic rating'] >= 90 and  # 90+ on Metacritic
            film['rt rating'] >= 90):  # 90+ on Rotten Tomatoes
            title = film['title']
            year = film['year']
            print(f"✓ {title} ({year})")
            print(f"  IMDB: {film['imdb rating']/10:.1f}/10")
            print(f"  Metacritic: {film['metacritic rating']}")
            print(f"  Rotten Tomatoes: {film['rt rating']}%")
            print(f"  Average Rating: {film['average rating']:.1f}")
            print("  ---------------")
            fufu_film = (title, year)
            fufu_films.append(fufu_film)

    if not fufu_films:
        print("\nNo films met all criteria (IMDB ≥ 7.5, Metacritic ≥ 90, RT ≥ 90)")
    else:
        print(f"\nFound {len(fufu_films)} films meeting all criteria!")
    
    return fufu_films

def main():
    # Get films and their ratings using APIs
    films = get_films()
    films_with_relevant_ratings = get_films_with_relevant_ratings(films)
    fufufilms = get_fufufilms(films_with_relevant_ratings)

    for film in fufufilms:
        print(f'{film[0]} ({film[1]})')
              
if __name__ == '__main__':
    main()