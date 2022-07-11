# Generated by Django 3.2.14 on 2022-07-11 17:59

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('signup', '0003_alter_student_info'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='classperiod',
            name='day_of_week',
        ),
        migrations.AddField(
            model_name='classperiod',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 7, 11, 17, 59, 37, 256138, tzinfo=utc), verbose_name='date'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='classperiod',
            name='number',
            field=models.SmallIntegerField(default=0, verbose_name='period number'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='classperiodsignup',
            name='class_period',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_sign_ups', to='signup.classperiod'),
        ),
        migrations.AlterField(
            model_name='classperiodsignup',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sign_ups', to='signup.student'),
        ),
        migrations.AddConstraint(
            model_name='classperiod',
            constraint=models.UniqueConstraint(fields=('date', 'number'), name='unique_date_number'),
        ),
    ]
