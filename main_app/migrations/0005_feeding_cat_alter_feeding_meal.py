# Generated by Django 4.0.2 on 2022-02-15 19:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0004_feeding'),
    ]

    operations = [
        migrations.AddField(
            model_name='feeding',
            name='cat',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='main_app.cat'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='feeding',
            name='meal',
            field=models.CharField(choices=[('B', 'Breakfast'), ('L', 'Lunch'), ('D', 'Dinner')], max_length=1),
        ),
    ]
