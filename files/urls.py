from django.urls import path
from . import views

urlpatterns = [
    path('',                         views.upload_zip,           name='upload_zip'   ),
    path('list/',                    views.list_files,           name='list_files'   ),
    path('download/<int:file_id>/',  views.download_file,        name='download_file'),
    path('extracted/<int:file_id>/', views.list_extracted_files, name='list_extracted_files'),
    path('delete/<int:file_id>/', views.delete_zip_file, name='delete_zip_file'),
    path('delete-extracted/<int:file_id>/<str:filename>/', views.delete_extracted_file, name='delete_extracted_file'),
] 