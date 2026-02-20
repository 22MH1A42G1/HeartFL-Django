import os
import csv
import random
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from accounts.models import User
from hospitals.models import Hospital, Dataset

FEATURE_COLUMNS = ['age','sex','cp','trestbps','chol','fbs','restecg','thalach','exang','oldpeak','slope','ca','thal','target']

def generate_sample_csv(n=100):
    rows = []
    for _ in range(n):
        age = random.randint(30, 75)
        sex = random.randint(0, 1)
        cp = random.randint(0, 3)
        trestbps = random.randint(90, 180)
        chol = random.randint(150, 350)
        fbs = random.randint(0, 1)
        restecg = random.randint(0, 2)
        thalach = random.randint(80, 200)
        exang = random.randint(0, 1)
        oldpeak = round(random.uniform(0, 5), 1)
        slope = random.randint(0, 2)
        ca = random.randint(0, 3)
        thal = random.randint(1, 3)
        target = random.randint(0, 1)
        rows.append([age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal, target])
    return rows

class Command(BaseCommand):
    help = 'Create sample data for HeartFL'

    def handle(self, *args, **options):
        # Create superadmin
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@heartfl.com', 'admin123', role='superadmin')
            self.stdout.write(self.style.SUCCESS('Created superadmin: admin / admin123'))

        # Create hospital admins and hospitals
        hospital_data = [
            ('City General Hospital', '123 Main St, New York, NY', 'admin_city', 'City@123'),
            ('Memorial Medical Center', '456 Oak Ave, Los Angeles, CA', 'admin_memorial', 'Memorial@123'),
            ('University Health System', '789 Pine Rd, Chicago, IL', 'admin_uni', 'Uni@123'),
        ]

        for hname, haddr, uname, upass in hospital_data:
            if not User.objects.filter(username=uname).exists():
                hadmin = User.objects.create_user(uname, f'{uname}@heartfl.com', upass, role='hospital_admin')
                hospital, created = Hospital.objects.get_or_create(name=hname, defaults={'address': haddr, 'hospital_admin': hadmin})
                if created:
                    rows = generate_sample_csv(150)
                    csv_content = ','.join(FEATURE_COLUMNS) + '\n'
                    for row in rows:
                        csv_content += ','.join(str(v) for v in row) + '\n'
                    dataset = Dataset(hospital=hospital, rows_count=len(rows), status='ready')
                    dataset.csv_file.save(f'{uname}_data.csv', ContentFile(csv_content.encode()), save=True)
                    self.stdout.write(self.style.SUCCESS(f'Created hospital: {hname} with dataset'))

        # Create doctor
        if not User.objects.filter(username='doctor1').exists():
            User.objects.create_user('doctor1', 'doctor1@heartfl.com', 'Doctor@123', role='doctor')
            self.stdout.write(self.style.SUCCESS('Created doctor: doctor1 / Doctor@123'))

        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
