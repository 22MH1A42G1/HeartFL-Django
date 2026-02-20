"""
Database Management Utilities for HeartFL Admin
Provides export, import, backup, and cleanup functionality
"""
import csv
import json
from io import StringIO, BytesIO
from django.http import HttpResponse
from django.db import models
from datetime import datetime


class DatabaseUtilities:
    """Utilities for database operations"""
    
    @staticmethod
    def export_to_csv(queryset, filename=None):
        """Export queryset to CSV"""
        try:
            if not queryset.exists():
                return None
            
            model = queryset.model
            # Get only simple fields, exclude methods and complex relationships
            fields = []
            for f in model._meta.get_fields():
                if f.name not in ['id'] and not f.many_to_many and not f.one_to_many:
                    fields.append(f.name)
            
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{filename or model.__name__}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
            
            writer = csv.DictWriter(response, fieldnames=['id'] + fields)
            writer.writeheader()
            
            for obj in queryset:
                row = {'id': obj.id}
                for field in fields:
                    try:
                        value = getattr(obj, field, '')
                        if hasattr(value, 'id'):  # Foreign key
                            row[field] = value.id
                        else:
                            row[field] = str(value) if value is not None else ''
                    except:
                        row[field] = ''
                writer.writerow(row)
            
            return response
        except Exception as e:
            return None
    
    @staticmethod
    def export_to_json(queryset, filename=None):
        """Export queryset to JSON"""
        try:
            if not queryset.exists():
                return None
            
            model = queryset.model
            data = []
            
            for obj in queryset:
                obj_data = {'id': obj.id}
                for field in model._meta.get_fields():
                    if field.name in ['id'] or field.many_to_many or field.one_to_many:
                        continue
                    try:
                        value = getattr(obj, field.name, None)
                        if hasattr(value, 'id'):
                            obj_data[field.name] = value.id
                        else:
                            obj_data[field.name] = str(value) if value is not None else None
                    except:
                        pass
                data.append(obj_data)
            
            response = HttpResponse(json.dumps(data, indent=2, default=str), content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="{filename or model.__name__}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json"'
            
            return response
        except Exception as e:
            return None
    
    @staticmethod
    def get_model_statistics():
        """Get statistics for all models"""
        from django.apps import apps
        
        stats = {}
        for app_config in apps.get_app_configs():
            if app_config.name.startswith('django'):
                continue
            stats[app_config.verbose_name] = {}
            for model in app_config.get_models():
                count = model.objects.count()
                stats[app_config.verbose_name][model.__name__] = count
        
        return stats
    
    @staticmethod
    def cleanup_old_records(model, days=30):
        """Delete records older than specified days"""
        from django.utils import timezone
        from datetime import timedelta
        
        if hasattr(model, 'created_at'):
            cutoff_date = timezone.now() - timedelta(days=days)
            deleted_count, _ = model.objects.filter(created_at__lt=cutoff_date).delete()
            return deleted_count
        return 0
    
    @staticmethod
    def get_database_size():
        """Get approximate database size"""
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size();")
            try:
                result = cursor.fetchone()
                return result[0] if result else 0
            except:
                return 0
