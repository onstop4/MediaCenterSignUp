# Generated by Django 3.2.14 on 2022-07-24 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('signup', '0007_add_is_active_field_to_User'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classperiodsignup',
            name='date_attendance_confirmed',
            field=models.DateTimeField(blank=True, null=True, verbose_name='date attendance was confirmed'),
        ),
    ]