from django.db import models
import os
import shutil

# Create your models here.

class ZipFile(models.Model):
    file        = models.FileField(upload_to='zip_files/', max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField( blank=True, null=True)
    extracted_path = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"ZipFile {self.file.name} uploaded at {self.uploaded_at}"

    def get_extracted_files(self):
        if self.extracted_path and os.path.exists(self.extracted_path):
            return [f for f in os.listdir(self.extracted_path) if os.path.isfile(os.path.join(self.extracted_path, f))]
        return []

    def delete_extracted_file(self, filename):
        if self.extracted_path and os.path.exists(self.extracted_path):
            file_path = os.path.join(self.extracted_path, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        return False

    def delete(self, *args, **kwargs):
        # Eliminar el archivo ZIP
        if self.file and os.path.exists(self.file.path):
            os.remove(self.file.path)
        
        # Eliminar el directorio de archivos descomprimidos
        if self.extracted_path and os.path.exists(self.extracted_path):
            shutil.rmtree(self.extracted_path)
        
        super().delete(*args, **kwargs)
