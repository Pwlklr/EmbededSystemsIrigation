# Generated by Django 4.2.11 on 2024-12-11 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aplikacja', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='scheduleevent',
            name='status',
            field=models.CharField(choices=[('planned', 'Planowe'), ('canceled', 'Odwołane'), ('extra', 'Dodatkowe')], default='planned', max_length=10),
        ),
    ]
