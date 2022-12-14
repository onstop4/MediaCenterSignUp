# Generated by Django 3.2.14 on 2022-07-08 22:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('signup', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClassPeriod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_of_week', models.SmallIntegerField(verbose_name='day of week')),
                ('max_student_count', models.PositiveIntegerField(verbose_name='maximum students allowed')),
            ],
        ),
        migrations.CreateModel(
            name='ClassPeriodSignUp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(choices=[('L', 'lunch'), ('S', 'study hall')], max_length=1)),
                ('class_period', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='signup.classperiod')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='signup.student')),
            ],
        ),
        migrations.AddConstraint(
            model_name='classperiodsignup',
            constraint=models.UniqueConstraint(fields=('student', 'class_period'), name='unique_sign_up_class_period'),
        ),
    ]
