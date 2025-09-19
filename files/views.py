from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .models import ZipFile
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import os
import zipfile
from pathlib import Path

# Create your views here.

def upload_zip(request):
    if request.method == 'POST':
        try:
            file = request.FILES.get('file')
            description = request.POST.get('description', '')
            
            if not file:
                return HttpResponse('Por favor, selecciona un archivo.', status=400)
            
            # Verificar la extensión del archivo
            if not file.name.lower().endswith('.zip'):
                return HttpResponse(f'El archivo {file.name} no es un archivo ZIP válido. La extensión debe ser .zip', status=400)
            
            # Verificar el tamaño del archivo
            if file.size > settings.MAX_UPLOAD_SIZE:
                return HttpResponse('El archivo es demasiado grande. El tamaño máximo permitido es 10MB.', status=400)
            
            # Intentar abrir el archivo como ZIP para verificar que sea válido
            try:
                with zipfile.ZipFile(file) as zip_ref:
                    # Verificar que el archivo ZIP no esté vacío
                    if not zip_ref.namelist():
                        return HttpResponse('El archivo ZIP está vacío.', status=400)
            except zipfile.BadZipFile:
                return HttpResponse('El archivo no es un archivo ZIP válido o está corrupto.', status=400)
            
            # Guardar el archivo
            zip_file = ZipFile(file=file, description=description)
            zip_file.save()
            
            # Crear directorio para archivos descomprimidos
            base_name = os.path.splitext(os.path.basename(file.name))[0]
            extract_path = os.path.join(settings.MEDIA_ROOT, 'extracted_files', base_name)
            os.makedirs(extract_path, exist_ok=True)
            
            # Descomprimir el archivo
            with zipfile.ZipFile(zip_file.file.path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            
            # Guardar la ruta de descompresión
            zip_file.extracted_path = extract_path
            zip_file.save()
            
            return redirect('list_files')
        except Exception as e:
            return HttpResponse(f'Error al subir el archivo: {str(e)}', status=500)
    
    return render(request, 'files/upload_form.html')

def list_files(request):
    files_list = ZipFile.objects.all().order_by('-uploaded_at')
    page = request.GET.get('page', 1)
    paginator = Paginator(files_list, 10)  # 10 archivos por página
    
    try:
        files = paginator.page(page)
    except PageNotAnInteger:
        files = paginator.page(1)
    except EmptyPage:
        files = paginator.page(paginator.num_pages)
    
    return render(request, 'files/list_files.html', {
        'files': files,
        'page_obj': files
    })

def download_file(request, file_id):
    try:
        zip_file = ZipFile.objects.get(id=file_id)
        file_path = zip_file.file.path
        
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/zip')
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                return response
        else:
            return HttpResponse('El archivo no existe.', status=404)
    except ZipFile.DoesNotExist:
        return HttpResponse('El archivo no existe.', status=404)

def list_extracted_files(request, file_id):
    try:
        zip_file = ZipFile.objects.get(id=file_id)
        extracted_files = zip_file.get_extracted_files()
        
        # Paginación para archivos descomprimidos
        page = request.GET.get('page', 1)
        paginator = Paginator(extracted_files, 20)  # 20 archivos por página
        
        try:
            files = paginator.page(page)
        except PageNotAnInteger:
            files = paginator.page(1)
        except EmptyPage:
            files = paginator.page(paginator.num_pages)
        
        return render(request, 'files/extracted_files.html', {
            'zip_file': zip_file,
            'extracted_files': files,
            'page_obj': files
        })
    except ZipFile.DoesNotExist:
        return HttpResponse('El archivo no existe.', status=404)

def delete_zip_file(request, file_id):
    try:
        zip_file = ZipFile.objects.get(id=file_id)
        zip_file.delete()
        return JsonResponse({'status': 'success'})
    except ZipFile.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Archivo no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def delete_extracted_file(request, file_id, filename):
    try:
        zip_file = ZipFile.objects.get(id=file_id)
        if zip_file.delete_extracted_file(filename):
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'message': 'Archivo no encontrado'}, status=404)
    except ZipFile.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Archivo ZIP no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
