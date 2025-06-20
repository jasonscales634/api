# Generated by Django 3.1.14 on 2025-06-18 08:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('affiliate', '0003_affiliatedailystat'),
    ]

    operations = [
        migrations.AlterField(
            model_name='affiliatedailystat',
            name='affiliate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_stats', to='affiliate.affiliateprofile'),
        ),
        migrations.AlterUniqueTogether(
            name='affiliatedailystat',
            unique_together={('affiliate', 'date')},
        ),
    ]
