from django.shortcuts import render
from django.http import HttpResponse
import matplotlib.pyplot as plt 
import matplotlib 
import io 
import urllib, base64 
import numpy as np
import os
from dotenv import load_dotenv
from openai import OpenAI

from .models import Movie

# Create your views here.

def home(request):
    searchTerm = request.GET.get('searchMovie')
    if searchTerm:
        movies = Movie.objects.filter(title__icontains=searchTerm)
    else:
        movies = Movie.objects.all()
    return render(request, 'home.html', {'searchTerm': searchTerm, 'movies': movies})

def about(request):
    return render(request, 'about.html')

def signup(request):
    email = request.GET.get("email")
    return render(request, 'signup.html', {'email': email})

def statistics_view(request): 
    matplotlib.use('Agg') 
    all_movies = Movie.objects.all() 

    movie_counts_by_year = {} 
    for movie in all_movies: 
        year = movie.year if movie.year else "None" 
        if year in movie_counts_by_year: 
            movie_counts_by_year[year] += 1 
        else: 
            movie_counts_by_year[year] = 1 

    bar_width = 0.5 
    bar_positions = range(len(movie_counts_by_year)) 
    plt.bar(bar_positions, movie_counts_by_year.values(), width=bar_width, align='center') 
    plt.title('Movies per year') 
    plt.xlabel('Year') 
    plt.ylabel('Number of movies') 
    plt.xticks(bar_positions, movie_counts_by_year.keys(), rotation=90) 
    plt.subplots_adjust(bottom=0.3) 
    buffer = io.BytesIO() 
    plt.savefig(buffer, format='png') 
    buffer.seek(0) 
    plt.close() 
    image_png = buffer.getvalue() 
    buffer.close() 
    graphic = base64.b64encode(image_png).decode('utf-8') 

    genre_counts = {}
    for movie in all_movies:
        if movie.genre:
            genres_list = [g.strip() for g in movie.genre.split(',')]
            for genre in genres_list:
                if genre in genre_counts:
                    genre_counts[genre] += 1
                else:
                    genre_counts[genre] = 1
        else:
            if "None" in genre_counts:
                genre_counts["None"] += 1
            else:
                genre_counts["None"] = 1

    top_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:9]
    genres, counts = zip(*top_genres) if top_genres else ([], [])

    plt.figure()
    plt.bar(genres, counts, width=bar_width, align='center', color='green')
    plt.title('Movies per genre (Top 9)')
    plt.xlabel('Genre')
    plt.ylabel('Number of movies')
    plt.xticks(rotation=45)
    plt.tight_layout()
    buffer_genre = io.BytesIO()
    plt.savefig(buffer_genre, format='png')
    buffer_genre.seek(0)
    plt.close()
    image_png_genre = buffer_genre.getvalue()
    buffer_genre.close()
    graphic_genre = base64.b64encode(image_png_genre).decode('utf-8')

    return render(request, 'statistics.html', {
        'graphic': graphic,
        'graphic_genre': graphic_genre
    })


def cosine_similarity(a, b):
    """Calculate cosine similarity between two vectors."""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def movie_search(request):
    """Search for movies using natural language prompts and OpenAI embeddings."""
    best_movie = None
    max_similarity = 0
    prompt = None
    error_message = None
    
    if request.method == 'POST':
        prompt = request.POST.get('prompt', '').strip()
        
        if prompt:
            try:
                load_dotenv('openAI.env')
                client = OpenAI(api_key=os.environ.get('openai_apikey'))
                
                response = client.embeddings.create(
                    input=[prompt],
                    model="text-embedding-3-small"
                )
                prompt_emb = np.array(response.data[0].embedding, dtype=np.float32)
                
                for movie in Movie.objects.all():
                    try:
                        movie_emb = np.frombuffer(movie.emb, dtype=np.float32)
                        similarity = cosine_similarity(prompt_emb, movie_emb)
                        
                        if similarity > max_similarity:
                            max_similarity = similarity
                            best_movie = movie
                    except Exception as e:
                        continue
                        
            except Exception as e:
                error_message = f"Error processing request: {str(e)}"
        else:
            error_message = "Please enter a search prompt."
    
    context = {
        'prompt': prompt,
        'best_movie': best_movie,
        'similarity': max_similarity,
        'error_message': error_message
    }
    
    return render(request, 'movie_search.html', context)