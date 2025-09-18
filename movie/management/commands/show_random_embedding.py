import os
import numpy as np
from django.core.management.base import BaseCommand
from movie.models import Movie
import random

class Command(BaseCommand):
    help = "Muestra los embeddings de una película seleccionada al azar"

    def handle(self, *args, **kwargs):
        movies = Movie.objects.exclude(emb=None)
        if not movies.exists():
            self.stderr.write("No hay películas con embeddings generados.")
            return

        movie = random.choice(list(movies))
        self.stdout.write(f"Película seleccionada: {movie.title}")
        emb = np.frombuffer(movie.emb, dtype=np.float32)
        self.stdout.write(f"Embeddings:\n{emb}")
