import os
from django.core.management.base import BaseCommand
from movie.models import Movie

class Command(BaseCommand):
    help = "Actualiza la imagen de cada película desde la carpeta media/movie/images/"

    def handle(self, *args, **kwargs):
        images_folder = os.path.join('media', 'movie', 'images')
        updated_count = 0
        not_found = 0

        for movie in Movie.objects.all():
            image_filename = f"m_{movie.title}.png"
            image_path = os.path.join(images_folder, image_filename)

            if os.path.exists(image_path):
                movie.image = os.path.join('movie/images', image_filename)
                movie.save()
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f"Imagen actualizada: {movie.title}"))
            else:
                not_found += 1
                self.stderr.write(f"Imagen no encontrada para: {movie.title}")

        self.stdout.write(self.style.SUCCESS(f"Total imágenes actualizadas: {updated_count}"))
        self.stdout.write(self.style.WARNING(f"Películas sin imagen: {not_found}"))
